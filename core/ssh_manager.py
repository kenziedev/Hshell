# core/ssh_manager.py
# SSH 연결 및 포트 포워딩 기능 포함 + 비밀번호 복호화 지원

import logging
import os
import select
import socket
import threading

import paramiko

from core.app_paths import get_app_data_dir
from core.encryption import decrypt_password  # 🔐 복호화 함수 추가

logger = logging.getLogger(__name__)


class PersistingHostKeyPolicy(paramiko.MissingHostKeyPolicy):
    """
    신규 호스트 키는 사용자 데이터 디렉토리의 known_hosts 파일에 저장하고,
    이후부터는 해당 키를 검증하도록 하는 정책.
    """

    def __init__(self, known_hosts_path: str):
        self.known_hosts_path = known_hosts_path

    def missing_host_key(self, client, hostname, key):
        logger.warning(
            "[!] 새 호스트 키 감지: %s (%s) - known_hosts에 저장합니다.",
            hostname,
            key.get_name(),
        )
        host_keys = client.get_host_keys()
        host_keys.add(hostname, key.get_name(), key)
        try:
            host_keys.save(self.known_hosts_path)
        except OSError as exc:
            logger.error("known_hosts 저장 실패: %s", exc)


class SSHManager:
    def __init__(self, server_info):
        """
        server_info: servers.json에서 불러온 하나의 서버 딕셔너리
        """
        self.server_info = server_info
        self.client = None
        self.transport = None
        self.tunnel_threads = []
        self._tunnel_controls = []
        self._tunnel_servers = []
        self._tunnel_lock = threading.Lock()
        self.known_hosts_file = os.path.join(get_app_data_dir(), "known_hosts")

    def connect(self):
        """
        SSH 연결을 시도하고, 연결되면 터널링 스레드 시작
        """
        try:
            self._stop_all_tunnels()

            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            if os.path.exists(self.known_hosts_file):
                self.client.load_host_keys(self.known_hosts_file)
            self.client.set_missing_host_key_policy(
                PersistingHostKeyPolicy(self.known_hosts_file)
            )

            # 🔐 비밀번호 복호화
            try:
                decrypted_password = decrypt_password(self.server_info["password"])
            except Exception as e:
                print(f"[!] 비밀번호 복호화 실패: {e}")
                return False

            self.client.connect(
                hostname=self.server_info["host"],
                port=self.server_info["port"],
                username=self.server_info["username"],
                password=decrypted_password,
                timeout=5
            )

            self.transport = self.client.get_transport()
            self.transport.set_keepalive(30)

            print(f"[+] {self.server_info['name']} 서버 연결 성공!")

            # 터널링 정보가 있으면 모두 시작
            for tunnel in self.server_info.get("tunnels", []):
                stop_event = threading.Event()
                thread = threading.Thread(
                    target=self._start_tunnel,
                    args=(tunnel, stop_event),
                    daemon=True,
                )
                thread.start()
                self.tunnel_threads.append(thread)
                self._tunnel_controls.append((thread, stop_event))

            return True

        except Exception as e:
            print(f"[!] {self.server_info['name']} 서버 연결 실패: {e}")
            return False

    def _start_tunnel(self, tunnel_info, stop_event: threading.Event):
        """
        로컬 → 원격 포트 포워딩 수행
        """
        local_port = tunnel_info["local"]
        remote_host = tunnel_info["remote_host"]
        remote_port = tunnel_info["remote_port"]
        tunnel_name = tunnel_info.get("name", "Unnamed")
        server = None

        try:
            print(f"[*] [{tunnel_name}] 포트포워딩 시작: localhost:{local_port} → {remote_host}:{remote_port}")

            # 로컬 서버 소켓 열기
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('127.0.0.1', local_port))
            server.listen(100)
            server.settimeout(1)

            with self._tunnel_lock:
                self._tunnel_servers.append(server)

            while not stop_event.is_set():
                try:
                    client_socket, addr = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break

                print(f"[+] [{tunnel_name}] 클라이언트 접속됨: {addr}")
                threading.Thread(
                    target=self._handle_connection,
                    args=(client_socket, remote_host, remote_port, tunnel_name),
                    daemon=True,
                ).start()

        except Exception as e:
            print(f"[!] [{tunnel_name}] 터널링 실패: {e}")
        finally:
            if server is not None:
                with self._tunnel_lock:
                    if server in self._tunnel_servers:
                        self._tunnel_servers.remove(server)
                try:
                    server.close()
                except OSError:
                    pass

    def _handle_connection(self, client_socket, remote_host, remote_port, tunnel_name):
        """
        클라이언트와 원격 서버 간 데이터 전송 중계
        """
        chan = None
        try:
            chan = self.transport.open_channel(
                "direct-tcpip",
                (remote_host, remote_port),
                client_socket.getsockname()
            )

            while True:
                r, _, _ = select.select([client_socket, chan], [], [])
                if client_socket in r:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    chan.send(data)
                if chan in r:
                    data = chan.recv(1024)
                    if not data:
                        break
                    client_socket.send(data)
        except Exception as e:
            print(f"[!] [{tunnel_name}] 포워딩 중 오류 발생: {e}")
        finally:
            client_socket.close()
            if chan:
                chan.close()
            print(f"[-] [{tunnel_name}] 연결 종료")

    def disconnect(self):
        """
        SSH 연결 종료
        """
        self._stop_all_tunnels()
        if self.client:
            self.client.close()
            print(f"[-] {self.server_info['name']} 서버 연결 종료됨.")
            self.client = None
            self.transport = None
            self.tunnel_threads = []

    def _stop_all_tunnels(self):
        for _, stop_event in self._tunnel_controls:
            stop_event.set()

        with self._tunnel_lock:
            for server in list(self._tunnel_servers):
                try:
                    server.close()
                except OSError:
                    pass
            self._tunnel_servers.clear()

        for thread, _ in self._tunnel_controls:
            if thread.is_alive():
                thread.join(timeout=2)

        self._tunnel_controls.clear()
        self.tunnel_threads = []

    def is_connected(self):
        """
        현재 연결 상태를 더 정확하게 확인
        """
        try:
            if not self.client or not self.transport:
                return False

            # 실제로 연결이 살아있는지 확인
            if not self.transport.is_active():
                return False

            try:
                self.transport.send_ignore()
            except EOFError:
                return False
            except OSError:
                return False

            return True
        except Exception:
            return False

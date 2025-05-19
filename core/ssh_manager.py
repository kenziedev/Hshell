# core/ssh_manager.py
# SSH 연결 및 포트 포워딩 기능 포함 + 비밀번호 복호화 지원

import paramiko
import threading
import socket
import select
from core.encryption import decrypt_password  # 🔐 복호화 함수 추가


class SSHManager:
    def __init__(self, server_info):
        """
        server_info: servers.json에서 불러온 하나의 서버 딕셔너리
        """
        self.server_info = server_info
        self.client = None
        self.transport = None
        self.tunnel_threads = []

    def connect(self):
        """
        SSH 연결을 시도하고, 연결되면 터널링 스레드 시작
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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
                thread = threading.Thread(
                    target=self._start_tunnel,
                    args=(tunnel,),
                    daemon=True
                )
                thread.start()
                self.tunnel_threads.append(thread)

            return True

        except Exception as e:
            print(f"[!] {self.server_info['name']} 서버 연결 실패: {e}")
            return False

    def _start_tunnel(self, tunnel_info):
        """
        로컬 → 원격 포트 포워딩 수행
        """
        local_port = tunnel_info["local"]
        remote_host = tunnel_info["remote_host"]
        remote_port = tunnel_info["remote_port"]
        tunnel_name = tunnel_info.get("name", "Unnamed")

        try:
            print(f"[*] [{tunnel_name}] 포트포워딩 시작: localhost:{local_port} → {remote_host}:{remote_port}")

            # 로컬 서버 소켓 열기
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('127.0.0.1', local_port))
            server.listen(100)

            while True:
                client_socket, addr = server.accept()
                print(f"[+] [{tunnel_name}] 클라이언트 접속됨: {addr}")
                threading.Thread(
                    target=self._handle_connection,
                    args=(client_socket, remote_host, remote_port, tunnel_name),
                    daemon=True
                ).start()

        except Exception as e:
            print(f"[!] [{tunnel_name}] 터널링 실패: {e}")

    def _handle_connection(self, client_socket, remote_host, remote_port, tunnel_name):
        """
        클라이언트와 원격 서버 간 데이터 전송 중계
        """
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
            chan.close()
            print(f"[-] [{tunnel_name}] 연결 종료")

    def disconnect(self):
        """
        SSH 연결 종료
        """
        if self.client:
            self.client.close()
            print(f"[-] {self.server_info['name']} 서버 연결 종료됨.")
            self.client = None
            self.transport = None
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
            
            # 간단한 명령을 실행해서 연결 상태 테스트
            self.client.exec_command('echo', timeout=1)
            return True
        except:
            return False

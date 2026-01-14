import ssl
import socket
from datetime import datetime
import concurrent.futures


def get_ssl_expiry_date(domain):
    """Get the SSL certificate expiry date of a domain."""
    # Connect to the domain
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
    conn.settimeout(3.0)
    
    try:
        conn.connect((domain, 443))
        ssl_info = conn.getpeercert()
        # Extract expiry date and convert to datetime object
        expiry_date = datetime.strptime(ssl_info['notAfter'], r'%b %d %H:%M:%S %Y %Z')
        return domain, expiry_date
    except Exception as e:
        return domain, f"Error fetching SSL info: {e}"
    finally:
        conn.close()


def check(*domains):
    """Check SSL expiry dates for a list of domains."""
    output = dict()
    if len(domains) == 1:
        if isinstance(domains[0], list):
            domains = domains[0]
        else:
            domain, result = get_ssl_expiry_date(domains[0])
            output[domain] = result
            return output

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(domains)) as executor:
        futures = [executor.submit(get_ssl_expiry_date, domain) for domain in domains]
        for future in concurrent.futures.as_completed(futures):
            domain, result = future.result()
            output[domain] = result
    return output



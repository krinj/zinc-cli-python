import subprocess


def user_owns_domain(domain_name: str):
    cmd = f"aws route53domains get-domain-detail --domain-name {domain_name} --region us-east-1 --output json"
    result = subprocess.run(cmd.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return_code = result.returncode
    is_domain_owned = return_code == 0
    print(f"Domain Check Result: {domain_name}, owned: {is_domain_owned}")

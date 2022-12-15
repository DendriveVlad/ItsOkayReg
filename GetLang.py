from requests import get


def get_country(ip):
    if ip[:3:] == "127":
        return "r"
    url = 'https://ipdb.ipcalc.co/ipdata/' + ip
    response = get(url, verify=False)
    data = response.json()["country"]["isoCode"]
    if data in ("RU", "KZ", "BY", "AM", "KG", "AZ", "MD", "UA"):
        return "r"
    return "e"

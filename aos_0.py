from aos.sdk.api import Client

client = Client(
    "https://10.52.137.219/api",
    verify_certificates=False,
)
client.login("admin", "Qazwsxedcrfv@123")

print(client.version.get()["version"])

for blueprint in client.blueprints.list() or []:
    print(blueprint["label"], blueprint["id"])
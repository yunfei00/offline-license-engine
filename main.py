from app.licensing import ensure_licensed, LicenseError

def main():
    try:
        lic = ensure_licensed()
    except LicenseError as e:
        print("授权失败：", e)
        return

    print("授权通过：", lic.get("customer", ""))
    # IMPORTANT: keep concurrency_handle alive (do not overwrite lic dict)
    # TODO: start your app UI here

if __name__ == "__main__":
    main()

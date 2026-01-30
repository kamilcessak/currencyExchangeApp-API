import requests
from decimal import Decimal
from datetime import date
from app.models.rate import Rate

NBP_API_URL = "http://api.nbp.pl/api/exchangerates/tables/A/?format=json"

async def sync_rates_with_nbp():
    try:
        response = requests.get(NBP_API_URL, timeout=5)
        response.raise_for_status()

        data = response.json()

        rates_list = data[0]["rates"]

        count = 0
        for item in rates_list:
            code = item["code"]
            mid = item["mid"]

            decimal_rate = Decimal(str(mid))
            existing_rate = await Rate.find_one(Rate.currency_code == code)
            
            if existing_rate:
                existing_rate.rate = decimal_rate
                existing_rate.last_updated = date.today()
                await existing_rate.save()
            else:
                await Rate(
                    currency_code=code,
                    rate=decimal_rate,
                    last_updated=date.today()
                ).create()

            count += 1
        return count
    
    except Exception as e:
        print(f"Error syncing rates with NBP: {e}")
        return 0
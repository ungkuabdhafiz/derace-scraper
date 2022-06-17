import asyncio
import json
import os
from playwright.async_api import async_playwright

DERACE_BASE_URL = "https://derace.com"
MAX_HORSE_PAGE = 261
MAX_RACES_PAGE = 4748
HORSE_COUNT = 5618


class DeraceScraper:
    async def start(self, url, datadir):
        self.url = url
        self.datadir = datadir
        self.data = []
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def action(self):
        async with self.page.expect_event("websocket") as ws_info:
            await self.page.goto(self.url)

        self.ws = await ws_info.value
        self.on_web_socket()

    def handle_framereceived(self, payload):
        try:
            payload = json.loads(payload[2:][:-1].replace("\\", "")[1:][:-1])

        except:
            try:
                payload = json.loads(payload[2:][:-2].replace("\\", ""))
            except:
                pass

        try:
            if payload["msg"] == "result":
                result = payload["result"]
                self.data.append(result)

        except:
            pass

    def on_web_socket(self):
        self.ws.on("framereceived", lambda payload: self.handle_framereceived(payload))

    def save_data_to_file(self, file_name):

        if not os.path.exists(self.datadir):
            os.makedirs(self.datadir)

        self.output_file = os.path.join(self.datadir, file_name)
        with open(self.output_file, "w") as outfile:
            json.dump(self.data, outfile)

        self.data = []

    async def exit(self):
        await self.page.wait_for_timeout(30000)
        await self.browser.close()
        await self.playwright.stop()


class HorseScraper(DeraceScraper):
    async def action(self):
        for i in range(0, HORSE_COUNT):
            try:
                async with self.page.expect_event("websocket") as ws_info:
                    await self.page.goto(f"{self.url}/{i}")
            except Exception as e:
                print(e)
                continue

            self.ws = await ws_info.value
            self.on_web_socket()

            print(f"HorseScraper horse {i}")

            await self.page.wait_for_timeout(30000)
            self.save_data_to_file(f"{i}.json")


class HorsesScraper(DeraceScraper):
    async def action(self):
        try:
            async with self.page.expect_event("websocket") as ws_info:
                await self.page.goto(self.url)
        except Exception as e:
            print(e)

        self.ws = await ws_info.value
        self.on_web_socket()

        await self.page.wait_for_timeout(30000)
        self.save_data_to_file("1.json")

        for i in range(2, MAX_HORSE_PAGE + 1):
            print(f"HorsesScraper page {i}")
            await self.page.wait_for_timeout(5000)
            selector = f'a[aria-label="Page {i}"]'
            await self.page.click(selector)
            self.save_data_to_file(f"{i}.json")


class RacesScraper(DeraceScraper):
    async def action(self):
        try:
            async with self.page.expect_event("websocket") as ws_info:
                await self.page.goto(self.url)
        except Exception as e:
            print(e)

        self.ws = await ws_info.value
        self.on_web_socket()

        await self.page.wait_for_timeout(5000)
        self.save_data_to_file("1.json")

        for i in range(2, MAX_RACES_PAGE + 1):
            print(f"RacesScraper page {i}")
            await self.page.wait_for_timeout(5000)
            selector = f'a[aria-label="Page {i}"]'
            await self.page.click(selector)

            await self.page.wait_for_timeout(5000)

            selector = 'tr[class="is-clickable"]'
            loc = self.page.locator(selector)

            try:
                for j in range(await self.page.locator(selector).count()):
                    await loc.nth(j).click()
                    await self.page.wait_for_timeout(1000)
                    await loc.nth(j).click()
                    await self.page.wait_for_timeout(1000)
            except Exception as e:
                print(e)
                continue

            self.save_data_to_file(f"{i}.json")


class CurrentRaceScraper(DeraceScraper):
    async def action(self):
        try:
            async with self.page.expect_event("websocket") as ws_info:
                await self.page.goto(self.url)
        except Exception as e:
            print(e)

        self.ws = await ws_info.value
        self.on_web_socket()

        await self.page.wait_for_timeout(5000)

        selector = 'tr[class="is-clickable"]'
        loc = self.page.locator(selector)

        try:
            for i in range(await self.page.locator(selector).count()):
                await loc.nth(i).click()
                await self.page.wait_for_timeout(1000)
                await loc.nth(i).click()
                await self.page.wait_for_timeout(1000)
        except Exception as e:
            print(e)

        self.save_data_to_file("current_race.json")


async def get_horse():
    print("get_horse start")
    horse = HorseScraper()
    await horse.start(url=f"{DERACE_BASE_URL}/horse", datadir="data/horse")
    await horse.action()
    await horse.exit()
    print("get_horse done")


async def get_horses():
    print("get_horses start")
    horses = HorsesScraper()
    await horses.start(url=f"{DERACE_BASE_URL}/horses", datadir="data/horses")
    await horses.action()
    await horses.exit()
    print("get_horses done")


async def get_races():
    print("get_races start")
    races = RacesScraper()
    await races.start(url=f"{DERACE_BASE_URL}/races/results", datadir="data/races")
    await races.action()
    await races.exit()
    print("get_races done")


async def get_current_race():
    print("get_current_race start")
    current_race = CurrentRaceScraper()
    await current_race.start(url=f"{DERACE_BASE_URL}/races", datadir="data")
    await current_race.action()
    await current_race.exit()
    print("get_current_race done")


async def main():
    task1 = asyncio.create_task(get_horse())
    task2 = asyncio.create_task(get_horses())
    task3 = asyncio.create_task(get_races())
    task4 = asyncio.create_task(get_current_race())
    tasks = [task1, task2, task3, task4]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

import requests
import bs4 as bs
import sys


def main():
    scraper = WarcrafttavernScraper("mc")
    soupList = scraper.getPageSoupList()
    parser = WarcrafttavernParser(soupList)
    itemList = parser.getItemList()
    for item in itemList:
        print(item)


class WarcrafttavernScraper:
    baseUrl = "https://www.warcrafttavern.com/"

    def __init__(self, instance):
        self.path = self.__instancePath(instance)
        self.currentUrl = WarcrafttavernScraper.baseUrl + self.path

    def getPageSoupList(self):
        soupList = []
        while (soup := self.__nextSoup()) != None:
            soupList.append(soup)
        return soupList

    def __nextSoup(self):
        if self.currentUrl is None:
            return None
        soup = self.__getSoup(self.currentUrl)
        self.currentUrl = self.__getNextUrl(soup)
        return soup

    def __getSoup(self, url):
        r = requests.get(url)
        if not r.status_code == 200:
            sys.exit(f"get request failed with code {r.status_code}")
        soup = bs.BeautifulSoup(r.content, "html.parser")
        return soup

    def __getNextUrl(self, soup):
        result = soup.find("a", class_="wpv-filter-next-link", href=True)
        if result is None:
            return None
        return self.baseUrl + result["href"]

    def __instancePath(self, instance):
        if instance == "mc":
            return "/loot/molten-core/"
        else:
            sys.exit(
                f"Warcrafttavnern scraper given instance '{instance}' which is not supported"
            )


class WarcrafttavernParser:
    def __init__(self, soupList):
        self.itemList = []
        for soup in soupList:
            self.itemList.extend(self.__soupToItemList(soup))

    def getItemList(self):
        return self.itemList

    def __soupToItemList(self, soup):
        table = self.__soupToTable(soup)
        rows = table.find_all("tr")
        itemList = []
        for i, row in enumerate(rows):
            if len(row) == 0 or self.__isHeaderRow(row):
                continue
            itemList.append(self.__rowToItem(row))
        return itemList

    def __isHeaderRow(self, row):
        return row.find("th") is not None

    def __soupToTable(self, soup):
        return soup.find("table", class_="loot-table")

    def __rowToItem(self, row):
        tds = row.find_all("td")
        itemName = tds[0].text
        url = tds[0].find("a", href=True)["href"]
        # level = tds[1]
        # zone = tds[2]
        # lootAcqusition = tds[3]
        acquisitionName = tds[4].text
        itemSlot = tds[5].text
        itemType = tds[6].text
        dropChance = tds[7].text
        return Item(
            itemName.strip(),
            acquisitionName.strip(),
            itemSlot.strip(),
            itemType.strip(),
            dropChance.strip(),
            url.strip(),
        )


class Item:
    def __init__(
        self, name, acquisitionName, itemSlot, itemType, dropChance, sourceUrl
    ):
        self.name = name
        self.acquisitionName = acquisitionName
        self.itemSlot = itemSlot
        self.itemType = itemType
        self.dropChance = dropChance
        self.sourceUrl = sourceUrl

    def __str__(self):
        message = f"""
name:               {self.name}
acquisitionName:    {self.acquisitionName}
itemSlot:           {self.itemSlot}
itemType:           {self.itemType}
dropChance:         {self.dropChance}
sourceUrl:          {self.sourceUrl}"""
        return message


if __name__ == "__main__":
    main()

import scrapy

class ImdbSpider(scrapy.Spider):
    name = 'imdb_spider'

    start_urls = ['https://www.imdb.com/title/tt1439629/']

    def parse(self,response):
        """
        parses through the imdb page of the given show or movie.
        returns a parse request for the full cast & crew page on imdb
        """
        cast_and_crew_page = 'fullcredits'
        cast_url = response.urljoin(cast_and_crew_page)
        yield scrapy.Request(cast_url, callback = self.parse_full_credits)

    def parse_full_credits(self, response):
        """
        starting from the cast & crew page this function will crawl to the pages of listed actors
        """
        #a list of the partial urls for each actor
        actors_suffixes = [a.attrib['href'] for a in response.css("td.primary_photo a")]
        #the first part of the complete url for the actor
        prefix = "https://www.imdb.com"
        #the full url to the actor
        actors_url = [prefix + suffix for suffix in actors_suffixes]
        #crawling to each of the actor's page
        for url in actors_url:
            yield scrapy.Request(url, callback = self.parse_actor_page)

    def parse_actor_page(self, response):
        """
        starting from the actor's page, this function will yield a dictionary where the
        keys are the names of the actors and the values are a list of the films and shows 
        they have been on
        """
        actor_name = response.css("span.itemprop::text")[0].get()
        filmography = []
        filmography_listings = response.css("div.filmo-row")
        #for loop to go through each of the actors' work
        for filmo in filmography_listings:
            #seeing what the actor's role was in a certain project
            role = filmo.css("::attr(id)").get()
            #checking to see if they acted in said project
            if role[0:3] == 'act':
                media_name = filmo.css("a::text")[0].get()
                #removing any commas since we are putting the results in a csv file
                media_name = media_name.replace(",","")
                #adding the filmography to a list
                filmography.append(media_name)
        #what will be written into the csv file
        yield{"actor": actor_name, "movie_or_TV_name": filmography}
                
        
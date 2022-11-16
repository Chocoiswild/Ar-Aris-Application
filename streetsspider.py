import scrapy


class StreetSpider(scrapy.Spider):
    name = 'street-spider'
    form_url = "https://www.gpost.ge/help/postal-codes"
    request_url = "https://www.gpost.ge/help/FindPostalCode"
    start_urls = [form_url]
    postcodes = ['0100', '0101', '0102', '0103', '0104', '0105', '0107', '0108', '0109', '0112', '0113', '0114', '0117', '0118', '0119', '0120', '0121', '0131', '0132', '0133', '0136', '0137', '0141', '0143', '0144', '0145', '0148', '0151', '0152', '0153', '0154', '0158', '0159', '0160', '0162', '0163', '0165', '0167', '0168', '0171', '0172', '0177', '0178', '0179', '0180', '0181', '0182', '0183', '0186', '0189', '0190', '0191', '0192', '0193', '0194', '0197', '0198', '1054']

    

    def parse(self, response):
        # Define Tbilisi's postcodes
        
        # Extract the token
        token = response.css('input[name="__RequestVerificationToken"]::attr(value)').get()
        # Create a Python dict with the form values

        for code in self.postcodes:
            token = response.css('input[name="__RequestVerificationToken"]::attr(value)').get()
            data = {
                '__RequestVerificationToken': token,
                'regionTypeID': "1",
                'postalCodeSearchValue': code,
                'X-Requested-With': 'XMLHttpRequest',

            }
            # Submit a Post request to it
            yield scrapy.FormRequest(url=self.request_url, formdata=data, callback=self.parse_streets)

    def parse_streets(self, response):

        yield {
            "response": response.css('div.com-location-name::text').getall(),
            # 'code': response.css('div.com-postcode-name::text').get()
        }

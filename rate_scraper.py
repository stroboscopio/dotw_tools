
def get_rates(username, password, hotel_codes, start_check, end_check, los=1, prog=1, curr='413'):
    
    import requests
    import csv
    import re
    from bs4 import BeautifulSoup
    from datetime import datetime
    from datetime import timedelta
    

    # build request Session
    session = requests.Session()

    params = {'username':username, 'password':password, '_token':'Mb7NYFwRmTSwrPTKwpPLzgaYBVDaM4QGZxys91gT'}
    # post login   
    s = session.post('https://www.dotwconnect.com/_myadmin/login', params)
    # url elements
    start_date = datetime.strptime(start_check, '%Y-%m-%d')
    end_date = datetime.strptime(end_check, '%Y-%m-%d')
    
    hotel_array = []
    
    while start_date <= end_date:
        
        check_in = datetime.date(start_date)
        check_out = check_in+timedelta(days=los)
        
        for hotel_code in hotel_codes:
            
            base_url = 'http://www.dotwconnect.com/_myadmin/operations/getRoomTypes/'
            
            hotel_code_str = str(hotel_code + '?&destination=&PSearchId=' + hotel_code)
            
            date_str = str('&PSearchType=hotel&PLocationType=&fromDate=&fromDateFormatted=' + str(check_in) + '&toDate=&toDateFormatted=' + str(check_out))
            
            search_param = str('&numberOfNights=&adults%5B0%5D=2&children%5B0%5D=0&boardBasis%5B0%5D=-1&residence%5B0%5D=6&nationality%5B0%5D=6&propertyType=&starRating=&perPage=10&currency='+ curr +'&availability=-1&customerId=87974&allowedSingleWithChildren=1&itineraryCode=&bookedItnNumber=&customerCountry=6&passengerNationalityOrCountry=3&_token=')
            
            token = str(params.get('_token'))
            # build url
            url = str(base_url+hotel_code_str+date_str+search_param+token)
            
            # retrieve html
            print(datetime.now().time())
            rate_page = session.get(url)
            # do the soup
            rate_soup = BeautifulSoup(rate_page.text, 'html.parser')
            # find all the rate_containers (so, the rate entries in the page)
            rate_containers = rate_soup.find_all('div', {'class': ['booking-selection-row']})
            
            for rate_container in rate_containers:
                
                rate_array =  []
                
                rate_input = rate_container.find('input')  
                
                room_id = rate_input.attrs.get('value')
                
                room_currency = rate_input.attrs.get('data-currency')
                
                room_items = rate_input.find_next_sibling('label').text
                
                if rate_container.find('span', {'class':['label-danger']}) is None:
                    cxl_policy = 'Refundable'
                
                else:
                    cxl_policy = rate_container.find('span', {'class':['label-danger']}).text
                    
                if rate_container.find('a', {'class':['non-hover']}).find('span').text is None:
                    deadline_info = 'No Deadline Info'
                
                else:
                    deadline_info = rate_container.find('a', {'class':['non-hover']}).find('span').text.strip()
                    
                    if deadline_info.split(':')[0] == "Deadline":
                        
                        deadline_str = datetime.date(datetime.strptime(deadline_info.split(':',1)[1].strip(), '%a, %d %b %Y %H:%M:%S'))
                    
                    else:
                    
                        deadline_str = deadline_info
            # find rate_table
                rate_table = rate_container.find('div', {'class':['pricePerDay']}).find('table')
                
                table_head = rate_table.find_all('th')
                
                table_body = rate_table.find('tbody')
                               
                table_rows = table_body.find_all('tr')
                    
                for tr in table_rows:
                    row_cells = tr.find_all('td')
                    rate_date = datetime.date(datetime.strptime(row_cells[0].text, '%A %b, %d %Y'))
                                                           
                    if table_head[1].text == 'RateCode':
                        rate_code = row_cells[1].text
                        rate_price = row_cells[2].text
                        rate_board = row_cells[5].text.strip()
                        rate_availability = row_cells[6].text
                    
                    else:
                        rate_code = "NA"
                        rate_price = row_cells[1].text
                        rate_board = row_cells[4].text.strip()
                        rate_availability = row_cells[5].text
                        
                    rate_str = re.search(r'\d+\,*\d+\.*\d*', rate_price).group()
                    
                    room_name = room_items.split('[',1)[0]
                    
                    if re.search(r'\[(.*?)\]', room_items) is None:
                        room_provider = 'DOTW'
                    else:
                        room_provider = re.search(r'\[(.*?)\]', room_items).group()
                        
                    hotel_array.extend([(hotel_code, room_id, room_name, room_provider, cxl_policy, str(deadline_str), str(rate_date), \
                          rate_code, room_currency, rate_str, rate_board, rate_availability)])
                                    
        start_date += timedelta(days=prog)

    with open("rate_check_{}.csv".format(hotel_codes, check_in, check_out),"w+", newline='') as csv_file:
        
        csvWriter = csv.writer(csv_file,delimiter=',')
        csvWriter.writerow(["hotel_code", "room_id", "room_name", "room_provider", "cxl_policy", "deadline_info", "rate_date", \
                            "rate_code", "room_currency", "rate_price", "rate_board", "rate_availability"])
        
        for i in hotel_array:
            csvWriter.writerow(i)    
        csv_file.close()
        
    
        


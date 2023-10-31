import utils 

res = utils.get_nearest(13.075393, 80.214797)
address = res['results'][0]['address']
distance = "{0:.2f} Km".format(res['results'][0]['distance']/100)
m = utils.create_map(res)
print(m.get_root().render())
# m.save('map.html')
# with open('map.html', 'r') as mp:
#     map_html = mp.read()

# print(map_html)
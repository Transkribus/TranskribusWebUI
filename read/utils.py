
def crop(coords):
   # coords = region.get("Coords").get("@points")
    points = coords.split()	
    xmin=ymin=99999999 #TODO durh...
    xmax=ymax=0
    points = [map(int, point.split(',')) for point in points]
    #boo two loops! but I like this one above here...
    #TODO woops... I actually need this to give the x-off y-off width and height...
    for point in points:
	if point[1] > ymax : ymax=point[1]
	if point[1] < ymin : ymin=point[1]
	if point[0] > xmax : xmax=point[0]
	if point[0] < xmin : xmin=point[0]
    crop = {'x':xmin, 'y':ymin, 'w':(xmax-xmin), 'h': (ymax-ymin)}
    crop_str = str(crop.get('x'))+"x"+str(crop.get('y'))+"x"+str(crop.get('w'))+"x"+str(crop.get('h'))

    return crop_str


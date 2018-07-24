import csv

mqtt_broker_ip = '192.168.1.9'
mqtt_username = 'ionodes'
mqtt_key = '1jg?8jJ+Ut8,'


# degrees C to degrees F
def ctof(c):
    return (float(c) * 9 / 5) + 32


# returns a full MQTT address for a given IO Tag
def iolookup(tag):
    io_list = []
    with open('IO.txt') as io_file:
        for z in csv.DictReader(io_file):
            io_list.append(z)
    for t in io_list:
        if t["IOtag"] == tag:
            return "/".join(["io",t["Card"],t["Direction"],tag])
    return ""


if __name__ == "__main__":
    print(iolookup("TI101"))
    print(iolookup("TI100"))
    print(iolookup("spam"))
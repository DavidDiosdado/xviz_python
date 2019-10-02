import json

prisma1 = json.load(open("prisma.json"))
plantilla = json.load(open("state_update.json"))

plantilla["data"]["updates"][0]["primitives"]["/object/shape"]["polygons"].append(prisma1)

prisma2 = json.load(open("prisma.json"))
prisma2["base"]["object_id"] = "object-2"
prisma2["vertices"] = [[55, 8, 0], [55, 3, 0], [65, 3, 0], [65, 8, 0]]
plantilla["data"]["updates"][0]["primitives"]["/object/shape"]["polygons"].append(prisma2)

print(plantilla["data"]["updates"][0]["primitives"]["/object/shape"]["polygons"])

for i in range(6):
    plantilla["data"]["updates"][0]["primitives"]["/object/shape"]["polygons"][0]["vertices"] = [[i, 15, 0], [i, 10, 0], [i + 10, 10, 0], [i + 10, 15, 0]]
    plantilla["data"]["updates"][0]["primitives"]["/object/shape"]["polygons"][1]["vertices"] = [[i, 8, 0], [i, 3, 0], [i + 10, 3, 0], [i + 10, 8, 0]]
    with open(str(i + 2) + '-frame.json', 'w') as file:
        json.dump(plantilla, file)

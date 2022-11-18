from api_service import load_retail_food

# href = "/retail/azbuka_vkusa/catalog/2544?placeSlug=azbukavkusa_serafimovicha_2"
# o = urlparse(href)
# xs = o.path.split("/")
# x = xs[len(xs) - 1]
# print(x)

category_ids = [2544]
slug = "azbukavkusa_serafimovicha_2"
xs = load_retail_food(category_ids, slug)
print(len(xs))
from collections import UserDict


class SliceDict(UserDict):
    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.data["medias"][key]
        return super().__getitem__(key)


def extract_hashtag_medias_top(response, *args, **kwargs):
    page_id = response["next_page_id"]
    one_by_two_item = []
    fill_items = []
    medias = []
    for section in response["response"]["sections"]:
        if section["layout_content"].get("one_by_two_item"):
            items = section["layout_content"]["one_by_two_item"]["clips"]["items"]
            one_by_two_item = [item["media"] for item in items]
        if section["layout_content"].get("fill_items"):
            fill_items = [
                item["media"] for item in section["layout_content"]["fill_items"]
            ]
        if section["layout_content"].get("medias"):
            medias = [item["media"] for item in section["layout_content"]["medias"]]

    items = SliceDict(
        {
            "one_by_two_item": one_by_two_item,
            "fill_items": fill_items,
            "medias": medias,
        }
    )
    if kwargs.get("skip_duplicates"):
        items = medias
    return items, page_id


extract_hashtag_medias_recent = extract_hashtag_medias_top
extract_hashtag_medias_clips = extract_hashtag_medias_top


def extract_user_clips(response, *args, **kwargs):
    page_id = response.get("next_page_id")
    items = [item["media"] for item in response["response"]["items"]]
    return items, page_id

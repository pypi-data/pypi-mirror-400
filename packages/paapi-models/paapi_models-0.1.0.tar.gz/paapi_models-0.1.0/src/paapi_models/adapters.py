from collections import Counter

import jq
from slugify import slugify

from .models import VinylModel

jq_title = jq.compile('.item_info.title.display_value')
jq_group = jq.compile('.item_info.classifications.product_group.display_value')
jq_binding = jq.compile('.item_info.classifications.binding.display_value')
jq_edition = jq.compile('.item_info.content_info.edition.display_value')
jq_language = jq.compile('.item_info.content_info.languages.display_values?[0].display_value')
jq_release_date = jq.compile('.item_info.product_info.release_date.display_value')
jq_brand = jq.compile('.item_info.by_line_info.brand.display_value')
jq_manufacturer = jq.compile('.item_info.by_line_info.manufacturer.display_value')
jq_images_primary = jq.compile('.images.primary')
jq_images_primary_url = jq.compile('.images.primary.large.url')
jq_images_variants = jq.compile('.images.variants')
jq_contributors = jq.compile('.item_info.by_line_info.contributors')
jq_ean = jq.compile('.item_info.external_ids.ea_ns.display_values')
jq_upc = jq.compile('.item_info.external_ids.up_cs.display_values')
jq_formats = jq.compile('.item_info.technical_info.formats.display_values')
jq_listings = jq.compile('.offers.listings')
jq_availability = jq.compile('.offers.listings?[0].availability')
jq_merchant = jq.compile('.offers.listings?[0].merchant_info.name')
jq_price = jq.compile('.offers.listings?[0].price')
jq_savings = jq.compile('.offers.listings?[0].price.savings')
jq_browse_nodes = jq.compile('.browse_node_info.browse_nodes')
jq_website_sales_rank = jq.compile('.browse_node_info.website_sales_rank.sales_rank')


class ItemAdapter:
    def __init__(self, item: dict):
        self.item = item

    def _first_value(self, jq_compiled):
        return jq_compiled.input_value(self.item).first()

    @property
    def asin(self) -> str:
        return self.item['asin']

    @property
    def url(self) -> str:
        return self.item['detail_page_url']

    @property
    def title(self) -> str:
        return self._first_value(jq_title) or ''

    @property
    def group(self) -> str:
        return self._first_value(jq_group) or ''

    @property
    def binding(self) -> str:
        return self._first_value(jq_binding) or ''

    @property
    def classification(self) -> str:
        return f'{self.group}:{self.binding}'

    @property
    def edition(self) -> str:
        return self._first_value(jq_edition) or ''

    @property
    def language(self) -> str:
        return self._first_value(jq_language) or ''

    @property
    def release_date(self) -> str:
        return (self._first_value(jq_release_date) or '')[:10]

    @property
    def year(self) -> int:
        date = self.release_date
        return int(date[:4]) if date[:4].isdigit() else 0

    @property
    def brand(self) -> str:
        return self._first_value(jq_brand) or ''

    @property
    def manufacturer(self) -> str:
        return self._first_value(jq_manufacturer) or ''

    @property
    def images_primary_url(self) -> str:
        return self._first_value(jq_images_primary_url) or ''

    @property
    def images_primary(self) -> dict:
        return self._first_value(jq_images_primary) or {}

    @property
    def images_variants(self) -> list[dict]:
        return self._first_value(jq_images_variants) or []

    @property
    def contributors(self) -> list[dict]:
        return self._first_value(jq_contributors) or []

    @property
    def contributor_names(self) -> list[dict]:
        return [x['name'] for x in self.contributors]

    @property
    def artist_names(self) -> list[str]:
        return [x['name'] for x in self.contributors if x.get('role_type') == 'artist']

    @property
    def performer_names(self) -> list[str]:
        return [x['name'] for x in self.contributors if x.get('role_type') == 'performer']

    @property
    def ean(self) -> str:
        values = self.ean_list
        return values[0] if values else ''

    @property
    def ean_list(self) -> list[str]:
        return self._first_value(jq_ean) or []

    @property
    def upc(self) -> str:
        values = self.upc_list
        return values[0] if values else ''

    @property
    def upc_list(self) -> list[str]:
        return self._first_value(jq_upc) or []

    @property
    def formats(self):
        return self._first_value(jq_formats)

    @property
    def availability(self) -> str:
        avail = self._first_value(jq_availability) or {}
        _type = (avail.get('type') or '').lower()
        _message = (avail.get('message') or '').lower()

        if _type == 'now':
            if 'out of stock' in _message:
                return 'out-of-stock'
            elif _message.startswith(('in stock', 'usually ship')):
                return 'in-stock'
            else:
                return ''

        if _type == 'preorderable':
            return 'preorderable'

        if _type == 'backorderable':
            return 'backorderable'

        return ''

    @property
    def merchant(self) -> str:
        return self._first_value(jq_merchant) or ''

    @property
    def price(self) -> dict:
        return self._first_value(jq_price) or {}

    @property
    def savings(self) -> dict:
        return self._first_value(jq_savings) or {}

    @property
    def price_amount(self) -> float:
        return self.price.get('amount') or 0

    @property
    def price_display_amount(self) -> str:
        return self.price.get('display_amount') or ''

    @property
    def savings_amount(self) -> float:
        return self.savings.get('amount') or 0

    @property
    def savings_display_amount(self) -> str:
        return self.savings.get('display_amount') or ''

    @property
    def savings_percentage(self) -> float:
        return self.savings.get('percentage') or 0

    @property
    def browse_nodes(self) -> list[dict]:
        return self._first_value(jq_browse_nodes) or []

    @property
    def sales_rank(self) -> int:
        return self._first_value(jq_website_sales_rank) or 9999999

    @property
    def sales_rank_summary(self) -> dict[str, int]:
        return {x['context_free_name']: x['sales_rank'] for x in self.browse_nodes if x.get('sales_rank')}

    @property
    def genres(self) -> list[str]:
        counter = Counter()
        for node in self.browse_nodes:
            name = self._get_genre_name(node)
            if name:
                counter[name] += 1

        # return in the order of frequency
        return [name for name, _ in counter.most_common()]

    @property
    def styles(self) -> list[str]:
        counter = Counter()
        for node in self.browse_nodes:
            name = self._get_style_name(node)
            if name:
                counter[name] += 1

        # return in the order of frequency
        return [name for name, _ in counter.most_common()]

    @property
    def barcodes(self) -> list[str]:
        _barcodes = []
        for x in self.ean_list + self.upc_list:
            if x and x not in _barcodes:
                _barcodes.append(x)
        return _barcodes

    @staticmethod
    def _is_genre_node(node: dict) -> bool:
        # genre if it's a direct child of "Music Styles"

        ancestor = node.get("ancestor")
        return ancestor.get("context_free_name") == "Music Styles" if ancestor else False

    @staticmethod
    def _is_style_node(node: dict) -> bool:
        # style if it's a grandchild of "Music Styles"

        ancestor = node.get("ancestor")
        return ItemAdapter._is_genre_node(ancestor) if ancestor else False

    @staticmethod
    def _get_genre_name(node: dict) -> str | None:
        node = node.copy()
        while node:
            if ItemAdapter._is_genre_node(node):
                return node.get("display_name") or node.get("context_free_name")
            node = node.get("ancestor")
        return None

    @staticmethod
    def _get_style_name(node: dict) -> str | None:
        node = node.copy()
        while node:
            if ItemAdapter._is_style_node(node):
                return node.get("display_name") or node.get("context_free_name")
            node = node.get("ancestor")
        return None


class VinylAdapter(ItemAdapter):

    def __init__(self, item: dict):
        super().__init__(item)

    @property
    def artists(self) -> list[str]:
        return self.artist_names or self.performer_names or self.contributor_names

    @property
    def labels(self) -> list[str]:
        seen = set()
        _labels = []
        for name in [self.brand, self.manufacturer]:
            s = slugify(name) if name else ''
            if s and s not in seen:
                seen.add(s)
                _labels.append(name)
        return _labels

    def to_model(self) -> VinylModel:
        return VinylModel.model_validate(self, from_attributes=True)

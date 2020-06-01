import enum


class SortType(enum.Enum):
    RECOMMENDED = 1
    LOW_PRICE = 2
    HIGH_PRICE = 3


class SearchQuery:
    query = """
        WITH order_headers AS 
        (
            SELECT 
                    COUNT(*) as count, api_orderheader.product_id
                FROM
                    api_orderheader
                WHERE
                    api_orderheader.active = TRUE AND 
                    (api_orderheader.payment_type IS NOT NULL OR api_orderheader.payment_type != '') AND
                    api_orderheader.order_status_id != 3 AND
                    api_orderheader.type_selling_id IS NOT NULL
                    {check_in_check_out}
                GROUP BY 
                    product_id
        )
        SELECT
            api_room.product_ptr_id, 
            api_room.room_id,
            api_product.name,
            api_product.description, 
            room_detail_view.price,  
            api_room.bedroom_total,
            api_room.guest_maximum,
            api_room.bathroom_total,
            api_room.sqm_room,
            api_room.rating,
            api_room.contact_person_name,
            api_room.contact_person_phone,
            api_apartment.id,
            api_apartment.name,
            room_detail_view.type_selling_id,
            room_detail_view.name,
            room_detail_view.id,
            order_headers.count,
            {ads_field}
        FROM
            api_room
        JOIN 
            api_apartment
        ON
            api_apartment.id = api_room.apartment_id
        JOIN 
            api_product
        ON 
            api_product.product_id = api_room.product_ptr_id
        JOIN	
            room_detail_view
        ON
            api_room.room_id = room_detail_view.room_id AND room_detail_view.type_selling_id = {type_booking}
        LEFT JOIN
            order_headers
        ON
            order_headers.product_id = api_product.product_id
        WHERE
            api_room.room_id {ads_non_ads} (SELECT room_id FROM ads_view) {filter_apartment}
        ORDER BY 
            {order_by}
        OFFSET {offset}
        LIMIT 8;

    """

    @classmethod
    def ads_query(cls, type_booking, check_in, check_out, offset, filter_by, order_by):
        if order_by == SortType.RECOMMENDED:
            query_order_by = "order_headers.count"
        elif order_by == SortType.LOW_PRICE:
            query_order_by = "room_detail_view.price"
        else:
            query_order_by = "room_detail_view.price desc"

        if filter_by != 0:
            filter_apartment = 'AND api_room.apartment_id = %d' % filter_by
        else:
            filter_apartment = ''

        if check_in is None or check_out is None:
            check_in_check_out = ''
        else:
            check_in_check_out = """
            AND (api_orderheader.check_in_time NOT BETWEEN to_date('{check_in}','ddMMyyyy') and to_date('{check_out}','ddMMyyyy') OR
                    api_orderheader.check_out_time NOT BETWEEN to_date('{check_in}','ddMMyyyy') and to_date('{check_out}','ddMMyyyy'))
            """.format(check_in=check_in, check_out=check_out)

        return cls.query.format(check_in_check_out=check_in_check_out, offset=offset, type_booking=type_booking,
                                order_by=query_order_by, ads_non_ads='IN', ads_field='TRUE AS ADS', filter_apartment=filter_apartment)

    @classmethod
    def non_ads_query(cls, type_booking, check_in, check_out, offset, filter_by, order_by):
        if order_by == SortType.RECOMMENDED:
            query_order_by = "order_headers.count"
        elif order_by == SortType.LOW_PRICE:
            query_order_by = "room_detail_view.price"
        else:
            query_order_by = "room_detail_view.price desc"

        if filter_by != 0:
            filter_apartment = 'AND api_room.apartment_id = %d' % filter_by
        else:
            filter_apartment = ''

        if check_in is None or check_out is None:
            check_in_check_out = ''
        else:
            check_in_check_out = """
            AND (api_orderheader.check_in_time NOT BETWEEN to_date('{check_in}','ddMMyyyy') and to_date('{check_out}','ddMMyyyy') OR
                    api_orderheader.check_out_time NOT BETWEEN to_date('{check_in}','ddMMyyyy') and to_date('{check_out}','ddMMyyyy'))
            """.format(check_in=check_in, check_out=check_out)

        return cls.query.format(check_in_check_out=check_in_check_out, offset=offset, type_booking=type_booking,
                                order_by=query_order_by, ads_non_ads="NOT IN", ads_field='FALSE AS ADS', filter_apartment=filter_apartment)

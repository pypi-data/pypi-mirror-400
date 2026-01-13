from forkast_py_client.types import OrderResponse, OrderResult, OrderData


class OrderMapper:
    """
    Mapper class for converting raw order data to typed objects
    """

    @staticmethod
    def map_order_response(raw_data: dict) -> OrderResponse:
        """
        Maps raw order data to an OrderResponse class.

        :param data: Raw order data from API
        :return: OrderResponse class
        """
        if not raw_data or "data" not in raw_data:
            return OrderResponse(
                success=False,
                error="Invalid response format: missing data property",
            )

        orders = [
            OrderData(
                orders_id=int(order["orders_id"]),
                orders_address=order["orders_address"],
                orders_type=int(order["orders_type"]),
                orders_side=int(order["orders_side"]),
                orders_outcome_type=int(order["orders_outcome_type"]),
                orders_status=int(order["orders_status"]),
                orders_price=order["orders_price"],
                orders_average_price=order["orders_average_price"],
                orders_amount=order["orders_amount"],
                orders_filled_amount=order["orders_filled_amount"],
                orders_remaining_amount=order["orders_remaining_amount"],
                orders_total=order["orders_total"],
                orders_created_at=order["orders_created_at"],
                orders_expired_at=order["orders_expired_at"],
                outcome_id=order["outcome_id"],
                outcome_outcome_type=int(order["outcome_outcome_type"]),
                outcome_title=order["outcome_title"],
                outcome_result=order["outcome_result"],
                user_id=order["user_id"],
                user_name=order["user_name"],
                user_avatar=order["user_avatar"],
                market_id=order["market_id"],
                market_event_id=int(order["market_event_id"]),
                market_title=order["market_title"],
                market_question=order["market_question"],
                market_image=order["market_image"],
            )
            for order in raw_data["data"]["data"]
        ]

        return OrderResponse(
            success=True,
            order_result=OrderResult(data=orders),
        )

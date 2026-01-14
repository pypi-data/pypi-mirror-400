def generate_kpi_card_changes(column_name, usd_change=False, percentage_change=False):
    """
    Generate SQL template for calculating KPI changes and percentage changes.

    Generates SQL snippets that calculate:
    - Current value
    - Absolute change (current - previous)
    - Percentage change (if percentage_change is True)
    - USD changes (if usd_change is True), also generates the same calculations for USD
      values.

    Args:
        column_name (str): Name of the column to generate changes for
        usd_change (bool, optional): Whether to include USD calculations. Defaults to
                                     False.
        percentage_change (bool, optional): Whether to include percentage change
                                            calculations. Defaults to False.

    Returns:
        str: SQL template string with calculations for changes and percentage changes

    Example:
        >>> generate_kpi_card_changes('total_supply')
        # Returns SQL template for total_supply and total_supply_usd changes
    """

    template = f"""
        , c.{column_name}
        , c.{column_name} - COALESCE(p.{column_name}, 0) AS {column_name}_change
    """

    if percentage_change:
        template += f"""
            , (
                (c.{column_name} - COALESCE(p.{column_name}, 0))
                / COALESCE(NULLIF(p.{column_name}, 0), NULLIF(c.{column_name}, 0))
            ) AS {column_name}_change_percentage
        """

    if usd_change:
        template += f"""
            , c.{column_name}_usd
            , c.{column_name}_usd - COALESCE(p.{column_name}_usd, 0)
                AS {column_name}_usd_change
        """
        if percentage_change:
            template += f"""
                , (
                    (c.{column_name}_usd - COALESCE(p.{column_name}_usd, 0))
                    / COALESCE(NULLIF(p.{column_name}_usd, 0), NULLIF(
                        c.{column_name}_usd, 0))
                ) AS {column_name}_usd_change_percentage
            """

    return template

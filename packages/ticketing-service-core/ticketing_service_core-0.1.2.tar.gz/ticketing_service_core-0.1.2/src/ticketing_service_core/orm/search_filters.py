"""
Allow dynamic specification of search criteria for SQLAlchemy queries
"""
class SearchFilters:
    """
    The SearchFilters class contains a list of desired search criteria and a set of helper
    functions for manupulating them
    """

    def __init__(self):
        self.criteria = []

    def equal(self, field, value):
        """
        Add an equality test to the search filters
        """

        self.__add_criteria(field, "==",value)

    def at_least(self, field, value):
        """
        Add a greater than or equal test to the search filters
        """

        self.__add_criteria(field, ">=",value)

    def at_most(self, field, value):
        """
        Add a less than or equal test to the search filters
        """

        self.__add_criteria(field, "<=",value)

    def before(self, field, value):
        """
        Alias for at_most to be used for datetime fields
        """

        self.at_most(field, value)

    def after(self, field, value):
        """
        Alias for at_least to be used for datetime fields
        """

        self.at_least(field, value)

    def __add_criteria(self, field, comparison, value):
        self.criteria.append({
            "field": field,
            "comparison": comparison,
            "value": value
        })

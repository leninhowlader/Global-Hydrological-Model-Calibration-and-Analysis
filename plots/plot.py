
class Plot:
    @staticmethod
    def generate_text_numbers(number_of_entries, is_capital=True):
        ## inner function
        def text_number(number):
            if number <= 0: return ''
            else:
                d, r = divmod(number, 26)
                if r == 0: return text_number(d - 1) + chr(start_ord + 25)
                else: return text_number(d) + chr(start_ord + number % 26 - 1)
        ## end [inner function]

        start_ord = ord('A')
        if not is_capital: start_ord = ord('a')

        return [text_number(x) for x in range(1, number_of_entries + 1)]
    ###
from .units import units,tens,scales
from .decorators import validate


class Convert:

    # def __init__(self):
    #     self.rev_units = {k:v for k,v in units.items()}
    #     self.rev_tens = {k:v for k,v in tens.items()}
    #     self.rev_scales = {k:v for k,v in sorted(scales.items(),reverse=True)}
    #     print(self.rev_scales)

    # @staticmethod
    def convert(self,*values):
        result = []
        for value in values:
            if isinstance(value,str):
                 result.append(self._convert_to_numeric(value))
            elif isinstance(value,int):
                 result.append(self._convert_to_string(value))
            else:
                raise TypeError(
                    f"Unsupported type: {type(value).__name__}"
                )
        return result




    @validate(str)
    def _convert_to_numeric(self,words_string:str)-> int:
        """
        :param self:self is the object of the class
        :param words_string: it takes the word in the string format
        This function is build to convert the given textual number to the numerical numbers
        """
        total = current = 0
        words =(word for word in words_string.lower().replace("-",' ').split() if word != "and")
        for word in words:
            if word in units:
                current += units[word]
            elif word in tens:
                current += tens[word]
            elif word in scales:
                if current ==0:
                    current = 1
                current *= scales[word]
                total += current
                current = 0
            else:
                raise ValueError(f"Invalid word: {word}")
        return total+current


    # @validate(int)
    # def _convert_to_string(self,number:int)-> str:
    #     for scale_name, scale_value in scales:
    #         if number >= scale_value:
    #             count = number // scale_value
    #             number =  number % scale_value



    @validate(int)
    def _convert_to_string(self, number: int) -> str:
        if number == 0:
            return "zero"

        parts = []

        # sort scales descending by value
        rev_scales = dict(sorted(scales.items(), key=lambda x: x[1], reverse=True))

        for scale_name, scale_value in rev_scales.items():
            if number >= scale_value:
                count = number // scale_value
                number = number % scale_value

                if scale_value >= 100:
                    # recursively convert the "count" part to string
                    count_str = self._convert_to_string(count)
                    parts.append(f"{count_str} {scale_name}")
                else:
                    # for hundreds or below, just append the number
                    parts.append(scale_name)

        # convert tens and units if remaining number
        if number > 0:
            if number < 20:
                parts.append([k for k,v in units.items() if v == number][0])
            else:
                tens_val = number // 10 * 10
                units_val = number % 10
                parts.append([k for k,v in tens.items() if v == tens_val][0])
                if units_val > 0:
                    parts.append([k for k,v in units.items() if v == units_val][0])

        return " ".join(parts)
    
from DialogModule import DialogModule
import lexems


def main():
    dm = DialogModule(food_dict=lexems.lex_food, modifier_dict=lexems.lex_modifier,
                      qty_dict=lexems.lex_qty, yesno_dict=lexems.lex_yesno)





if __name__ == '__main__':
    main()

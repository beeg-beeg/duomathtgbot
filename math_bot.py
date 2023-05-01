

from random import choice, randint
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Введите ваш токен бота
TOKEN = "6026789241:AAHI9iG0_Q0qJiFs4Xf9XoWX7hoZcrLEC0c"

def addpar(n):
    return f"{n}" if n >= 0 else f"({n})"

def generate_problem(difficulty):
    if difficulty == 1:
        ops = [["+", "-"]]
        num_range = (-10, 10)
    elif difficulty == 2:
        ops = [["+", "-"], ["*", "/"]]
        num_range = (-50, 50)
    else:
        ops = [["+", "-"], ["*", "/"]]
        num_range = (-100, 100)

    v3 = randint(*num_range)
    v4 = randint(*num_range)
    op3 = choice(ops[0])
    right = eval(f"{v3}{op3}{v4}")
    v1 = right * (randint(-50, 50+right + 100)//right + 1)
    v2 = right * (randint(-50-right-100, 50)//right + 1)
    op1 = choice(ops[0])
    op2 = choice(ops[min(difficulty - 1, 1)])

    problem = f"({addpar(v1)} {op1} {addpar(v2)}) {op2} ({addpar(v3)} {op3} {addpar(v4)})"
    return problem


def math_problem(update: Update, context: CallbackContext) -> None:
    difficulty = 1
    if context.args:
        try:
            difficulty = int(context.args[0])
            difficulty = min(max(difficulty, 1), 3)
        except ValueError:
            update.message.reply_text("Неверный формат сложности. Используйте число от 1 до 3.")
            return

    problem = generate_problem(difficulty)
    update.message.reply_text(problem)
    context.user_data['problem'] = problem
    context.user_data['answer'] = round(eval(problem))
    context.user_data['total_problems'] = context.user_data.get('total_problems', 0) + 1
    context.user_data['remaining_problems'] = 4
    context.user_data['correct_problems'] = []
    context.user_data['incorrect_problems'] = []

def check_answer(update: Update, context: CallbackContext) -> None:
    user_answer = update.message.text.strip()
    correct_answer = context.user_data.get('answer')
    problem = context.user_data.get('problem')

    if correct_answer is not None:
        if str(correct_answer) == user_answer:
            update.message.reply_text("Правильно! Ответ верный.")
            context.user_data['correct_answers'] = context.user_data.get('correct_answers', 0) + 1
            context.user_data['correct_problems'].append(problem)
        else:
            update.message.reply_text(f"Неправильно! Правильный ответ: {correct_answer}")
            context.user_data['incorrect_problems'].append(problem)

        remaining_problems = context.user_data.get('remaining_problems', 0)
        if remaining_problems > 0:
            difficulty = context.user_data.get('difficulty', 1)
            problem = generate_problem(difficulty)
            update.message.reply_text(problem)
            context.user_data['problem'] = problem
            context.user_data['answer'] = round(eval(problem))
            context.user_data['remaining_problems'] = remaining_problems - 1
        else:
            correct_problems = "\n".join(context.user_data['correct_problems'])
            incorrect_problems = "\n".join(context.user_data['incorrect_problems'])
            result_message = f"Результаты:\n\nПравильные ответы:\n{correct_problems}\n\nНеправильные ответы:\n{incorrect_problems}"
            update.message.reply_text(result_message)
    else:
        update.message.reply_text("Пожалуйста, сначала запросите задачу с помощью команды /problem.")


def stats(update: Update, context: CallbackContext) -> None:
    total_problems = context.user_data.get('total_problems', 0)
    correct_answers = context.user_data.get('correct_answers', 0)
    update.message.reply_text(f"Всего задач: {total_problems}\nПравильных ответов: {correct_answers}")

def start(update: Update, context: CallbackContext) -> None:
    user_first_name = update.effective_user.first_name
    welcome_message = f"""Привет, {user_first_name}! Этот бот предоставляет математические задачи для решения. 
Используйте команду /problem, чтобы получить задачу. Удачи!

Уровни сложности:
1 - сложение и вычитание, числа от -10 до 10
2 - сложение, вычитание, умножение и деление, числа от -50 до 50
3 - сложение, вычитание, умножение и деление, числа от -100 до 100

Для выбора уровня сложности, используйте команду /problem с аргументом, например: /problem 2"""
    update.message.reply_text(welcome_message)

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("problem", math_problem, pass_args=True))
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, check_answer))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

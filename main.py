import gspread
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler


def catch_job(tel_id:str) -> dict:
    # find job related to tel_id
    for job in sched.get_jobs():
        if job.args[0] == tel_id:
            jobs_dict[tel_id] = job.id
    return jobs_dict


async def get_message_ignored(tel_id: str, context: ContextTypes.DEFAULT_TYPE):
    # send message if ignored
    await context.bot.send_message(tel_id, "Проигнорировано")
    await context.bot.send_message(manager_id, f"Пользователь {tel_id} проигнорировал соообщение")
    if tel_id in jobs_dict.keys():
        sched.remove_job(jobs_dict[tel_id])
    del jobs_dict[tel_id]
    user = sh.find(str(tel_id))
    if user is not None:
        sh.update(f"{responses.address[0]}" + str(user.row), "Проигнорировано")


async def send_scheduled_message(tel_id: str, text: str, answer_time: int, context: ContextTypes.DEFAULT_TYPE):
    # add keyboard buttons
    buttons_list = [
        [InlineKeyboardButton(text="Выполнено1", callback_data="done")],
        [InlineKeyboardButton(text="Не сделано1", callback_data="not_done")]
    ]
    keyboard = InlineKeyboardMarkup(buttons_list)

    # send scheduled message
    await context.bot.send_message(tel_id, text, reply_markup=keyboard)
    sched.add_job(get_message_ignored, args=[tel_id, context], trigger="interval", seconds=int(answer_time))
    catch_job(tel_id)


async def send_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_row = tel_ids.row + 1
    await context.bot.send_message(update.effective_chat.id, "Напоминания назначены")

    while sh.acell(f"{tel_ids.address[0]}" + str(current_row)).value is not None:

        try:
            # get data from a row
            tel_id = sh.acell(f"{tel_ids.address[0]}" + str(current_row)).value
            text = sh.acell(f"{texts.address[0]}" + str(current_row)).value
            date = sh.acell(f"{dates.address[0]}" + str(current_row)).value
            time = sh.acell(f"{times.address[0]}" + str(current_row)).value
            answer_time = sh.acell(f"{answer_times.address[0]}" + str(current_row)).value
        except AttributeError:
            current_row += 1
            continue
        # ignore already registered users and get date/time
        if tel_id not in jobs_dict.keys():
            current_row += 1

            year = date.split("-")[0]
            month = date.split("-")[1]
            day = date.split("-")[2]

            hour = time.split(":")[0]
            minutes = time.split(":")[1]

            sched.add_job(send_scheduled_message, args=[tel_id, text, answer_time, context], trigger="cron", year=year,
                          month=month, day=day, hour=hour, minute=minutes)
            catch_job(tel_id)

        else:
            current_row += 1


async def default_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Для запуска напоминаний используется команда /send.")


async def positive_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = sh.find(str(update.effective_chat.id))
    if user is not None:
        if str(update.effective_chat.id) in jobs_dict.keys():
            sched.remove_job(jobs_dict[str(update.effective_chat.id)])
            del jobs_dict[str(update.effective_chat.id)]
        sh.update(f"{responses.address[0]}" + str(user.row), "Выполнено")
        await context.bot.send_message(update.effective_chat.id, "Ответ принят")
        await context.bot.send_message(manager_id, f"Пользователь {update.effective_chat.id} сообщил о выполнении")


async def negative_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = sh.find(str(update.effective_chat.id))
    if user is not None:
        if str(update.effective_chat.id) in jobs_dict.keys():
            sched.remove_job(jobs_dict[str(update.effective_chat.id)])
            del jobs_dict[str(update.effective_chat.id)]
        sh.update(f"{responses.address[0]}" + str(user.row), "Не сделано")
        await context.bot.send_message(update.effective_chat.id, "Ответ принят")
        await context.bot.send_message(manager_id, f"Пользователь {update.effective_chat.id} сообщил о не выполнении")


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "done":
        await positive_response(update, context)
    if update.callback_query.data == "not_done":
        await negative_response(update, context)


if __name__ == "__main__":
    with open('token.txt', 'r') as key:
        token = key.readline().strip()
    # get manager tel_id
    with open('manager_id.txt', 'r') as key:
        manager_id = key.readline().strip()

    # bot = telegram.Bot(token)
    sched = AsyncIOScheduler()
    sched.start()
    # connect to the service account
    gc = gspread.service_account(filename="gs_creds.json")
    # connect to sheet
    sh = gc.open("GS reminder bot").sheet1

    # find "heads" of data columns
    tel_ids = sh.find("tel_id")
    texts = sh.find("Текст")
    dates = sh.find("Дата(yyyy-mm-dd)")
    times = sh.find("Время(hh:mm)")
    answer_times = sh.find("Ожидание(сек)")
    responses = sh.find("Ответ")

    jobs_dict = {}

    application = ApplicationBuilder().token(token).build()

    run_handler = CommandHandler('send', send_reminders)
    default_handler = MessageHandler(filters.TEXT, default_response)
    buttons_handler = CallbackQueryHandler(buttons)

    application.add_handler(run_handler)
    application.add_handler(buttons_handler)
    application.add_handler(default_handler)

    application.run_polling()

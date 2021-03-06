#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on: Feb 6, 2017

import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime, time
import sys
import argparse

# Uncomment this to scrape goheels website to get UNC basketball results/schedule

# site = "http://www.goheels.com/SportSelect.dbml?SPSID=668157&SPID=12965"
# request = urllib.request.Request(site)
# opener = urllib.request.build_opener()
# page = opener.open(request)
#
# soup = BeautifulSoup(page, 'lxml')
#
# win_scrape = soup.find_all('td' , class_ = 'results')[0:]
# wins = []
# for i in win_scrape:
# 	win_name = i.get_text()
# 	win_name = win_name.strip('\n\t\t\t\t\t\t')
# 	wins.append(win_name)
# print(wins)


#
#
# school_scrape = soup.find_all('td' , class_ = 'opponent')[0:]
# schools = []
# for i in school_scrape:
# 	school_name = i.get_text()
# 	school_name = school_name.strip('\n\t\t\t\t\t\t')
# 	schools.append(school_name)
# print(schools)
#
#
# date_scrape = soup.find_all('td' , class_ = 'date')
# dates = []
# for i in date_scrape:
# 	date_name = i.get_text()
# 	date_name = date_name.strip('\n\t\t\t\t\t')
# 	dates.append(date_name)
# print(dates)
#
# time_scrape = soup.find_all('td' , class_ = 'time')
# times = []
# for i in time_scrape:
# 	time_name = i.get_text()
# 	time_name = time_name.strip('\n\t\t\t\t\t')
# 	times.append(time_name)
# print(times)

# Dealing with TBA in the datetime strpfmt: manually adding a 12PM tip time with a warning to check local listings
def game_times(times_list):
    new_game_time = []
    gametime_warning = []
    x = 0
    for game_time in times_list:
        if game_time == 'TBA':
            game_time = '12:00 PM'
            new_game_time.append(game_time)
            gametime_warning.append(x)
            x += 1
        else:
            new_game_time.append(game_time)
            x += 1
    return new_game_time, gametime_warning


# Remove symbols/whitespace from team names
def clean_opponent_names(schools):
    new_team_name = []
    for team in schools:
        if '*' in team:
            new_team_name.append(team[:-2])
        else:
            new_team_name.append(team)
    return new_team_name


# Help set year so the script can decipher which games were most recent -- basketball seasons run over '2' years
# so this was getting tricky (2016-2017 bball season)
def set_year(dates, new_game_time):
    now = datetime.now()
    # print(now)

    season_year2 = now.year
    season_year1 = now.year - 1
    # print(season_year1, season_year2)
    date_year = []
    for x in dates:
        end_months = ['Oct', 'Nov', 'Dec']
        if end_months[0] in x:
            date_year_str = str(x) + ' ' + str(season_year1) + ' ' + new_game_time[dates.index(x)]
            date_year.append(date_year_str)
        # print(date_year_str)
        elif end_months[1] in x:
            date_year_str = str(x) + ' ' + str(season_year1) + ' ' + new_game_time[dates.index(x)]
            date_year.append(date_year_str)
        # print(date_year_str)
        elif end_months[2] in x:
            date_year_str = str(x) + ' ' + str(season_year1) + ' ' + new_game_time[dates.index(x)]
            date_year.append(date_year_str)
        # print(date_year_str)
        else:
            date_year_str = str(x) + ' ' + str(season_year2) + ' ' + new_game_time[dates.index(x)]
            date_year.append(date_year_str)
    return date_year


# De-clutter dates so they are more easily read
def pretty_dates(year):
    dt_new = []
    dt_raw = []
    for x in year:
        dt = datetime.strptime(x, '%a, %b %d %Y %I:%M %p')
        dt_raw.append(dt)
        dt_fmt = dt.strftime('%a %m/%d')
        dt_new.append(dt_fmt)
    return dt_new, dt_raw


# Get the time of latest game to determine whether script should display most recent result or next game info
def get_latest_time(date_list, team_names, gametime_warning, results, dt_new):
    diff_list = []
    now_time = datetime.now()
    for z in date_list:
        # print('date list', x, 'now', now)
        diff = z - now_time

        # print('diff', diff)
        diff_days = diff.days
        # print('days', diff_days)
        diff_list.append(diff_days)
    diff_list_abs = [abs(number) for number in diff_list]
    gameday = min(diff_list_abs)
    indice_num = diff_list_abs.index(gameday)

    if diff_list[indice_num] >= 0:
        show_game = indice_num
        str1 = 'GAMEDAY: '
    elif 'L' in results[indice_num]:
        show_game = indice_num + 1
        str1 = 'GAMEDAY: '
    else:
        show_game = indice_num
        str1 = 'RESULT: '
    game_type_date = '%s%s' % (str1, dt_new[show_game])
    game_str = '\n%s\n%s\n%s' % (game_type_date.center(30, ' '), team_names[show_game].center(30, ' '),
                                 results[show_game].center(30, ' '))
    if show_game in gametime_warning:
        game_str += '\nCheck local listing for game time and opponent.\n'

    return game_str


# Print record information
def record(results, schools):
    wins = 0
    losses = 0
    remaining = 0
    for result in results:
        if 'W' in result:
            wins += 1
        elif 'L' in result:
            losses += 1
        else:
            if result == '':
                remaining += 1
            else:
                result_score = result.split('-')
                if result_score[0] > result_score[1]:
                    wins += 1
                else:
                    losses += 1
    for school in schools:
        if 'exh' in school:
            wins -= 1
    w_l_record = [wins, losses]
    return w_l_record


# Below is code that can be adapted to send email updates with this information

# Store schools and dates together as a tuple
# big_list = list(zip(schools, dates))
#
# target_results = []
#
# # If one of your target schools is in the results, put it in the text file
# for i in big_list:
# 	for j in target_schools:
# 		if j in i[0]:
# 			target_results.append("Result found for {} as {} on {}".format(j, i[0], i[1]))
#
# def output_writer(title):
# 	with open(path + title + '.txt', 'w') as f:
# 		for line in target_results:
# 			f.write(str(line) + "\n")
# 	f.close()
#
# output_writer('new_results')
#
# # Check for output file, correct if first run
# try:
# 	f = open(path + 'old_results.txt', 'r')
# except:
# 	output_writer('old_results')
# 	print('This is your first time running the script.\n'
# 		'Check the website for now, the next time you run it you will get updates.')
#
# updates = []
#
# with open(path + 'new_results.txt', 'r') as n:
# 	n = n.read()
# 	# If there is an update that wipes all your schools from the first page,
# 	# rewrite the file to avoid false flags
# 	if n == '\n' or n == '\n\n' or n == '':
# 		output_writer('old_results')
# 	n_l = n.split('\n')
# 	n_l_size = len(n_l)
# 	with open(path + 'old_results.txt', 'r') as o:
# 		o = o.read()
# 		o_l = o.split('\n')
# 		o_l_size = len(o_l)
# 		# Check for new results even if the same number of lines are present
# 		if o_l_size == n_l_size:
# 			for i in range(n_l_size):
# 				if n_l[i] != o_l[i]:
# 					updates.append(n_l[i])
# 			output_writer('old_results')
# 		# Stuck only checking the same amount of lines as the smaller file
# 		if o_l_size < n_l_size:
# 			for i in range(o_l_size):
# 				if n_l[i] != o_l[i]:
# 					updates.append(n_l[i])
# 			updates.append('There may be additional updates.')
# 			output_writer('old_results')
#
# if updates != []:
# 	print(updates)
# else:
# 	print('No new updates.')

# # GNOME integration for other Linux nerds
# import subprocess

# gnome_update = []

# for i in updates:
# 	if i == 'There may be additional updates':
# 		gnome_update.append(' + more')
# 	else:
# 		gnome_update.append(i[17:24])

# msg = ", ".join(str(i) for i in gnome_update)

# def send_message(message):
# 	subprocess.Popen(['notify-send', message])
# 	return
# if updates != []:
# 	send_message(msg)

# # Email functionality, you'll have to set it up yourself
# import smtplib

# gmail_user = 'your_username' + '@gmail.com'  
# gmail_password = 'your_password'

# outgoing = gmail_user  
# to = gmail_user 
# subject = 'School Admissions Update'  
# body = str(updates)

# email_text = """\  
# outgoing: {}  
# To: {}  
# Subject: {}

# {}
# """.format(outgoing, ", ".join(to), subject, body)

# try:  
#     server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#     server.ehlo()
#     server.login(gmail_user, gmail_password)
#     server.sendmail(outgoing, to, email_text)
#     server.close()

#     print 'Email sent!'
# except:  
#     print 'Something went wrong.'

if __name__ == '__main__':
    args = sys.argv
    parser = argparse.ArgumentParser(description='Display recent results or upcoming games for the University of '
                                                 'North Carolina mens basketball team')
    # parser.add_argument('input_file', help='transdecoder file')
    # parser.add_argument('-d', '--in_delim', help='input delimiter')
    # parser.add_argument('-s', '--sort', help='sort column <#> by <method> (ascending, descending, alphabetical')
    # parser.add_argument('-o', '--out_file', help='output file')
    # parser.add_argument('-c', '--column', help='columns #s (1-?) to write to output')
    # parser.add_argument('-hd', '--header', default='y', help='header? <y or n>')
    in_args = parser.parse_args()

    # Hard coded schedule/results info so that I wouldn't have to keep pulling data from website --
    # --> Remove the below lines to scrape current data and uncomment above. -- can put scraping in
    # a function when necessary

    schools_list = ['UNC Pembroke (exhibition)', 'Tulane', 'Chattanooga', 'Long Beach State',
               'Hawaii (8:00 PM HT/1:00 AM ET)',
               'Chaminade', 'Oklahoma State', 'Wisconsin', 'Indiana', 'Radford', 'Davidson', 'Tennessee', 'Kentucky',
               'Northern Iowa', 'Monmouth', 'Georgia Tech *', 'Clemson *', 'N.C. State *', 'Wake Forest *',
               'Florida State *', 'Syracuse *', 'Boston College *', 'Virginia Tech *', 'Miami *', 'Pittsburgh *',
               'Notre Dame *', 'Duke *', 'N.C. State *', 'Virginia *', 'Louisville *', 'Pittsburgh *', 'Virginia *',
               'Duke *', 'Miami (ACC Quarterfinal)', 'Duke ACC Semifinal', 'ACC Final']
    dates_list = ['Fri, Nov 04', 'Fri, Nov 11', 'Sun, Nov 13', 'Tue, Nov 15', 'Fri, Nov 18', 'Mon, Nov 21', 'Tue, Nov 22',
             'Wed, Nov 23', 'Wed, Nov 30', 'Sun, Dec 04', 'Wed, Dec 07', 'Sun, Dec 11', 'Sat, Dec 17', 'Wed, Dec 21',
             'Wed, Dec 28', 'Sat, Dec 31', 'Tue, Jan 03', 'Sun, Jan 08', 'Wed, Jan 11', 'Sat, Jan 14', 'Mon, Jan 16',
             'Sat, Jan 21', 'Thu, Jan 26', 'Sat, Jan 28', 'Tue, Jan 31', 'Sun, Feb 05', 'Thu, Feb 09', 'Wed, Feb 15',
             'Sat, Feb 18', 'Wed, Feb 22', 'Sat, Feb 25', 'Mon, Feb 27', 'Sat, Mar 04', 'Thu, Mar 09', 'Fri, Mar 10',
             'Sat, Mar 11']
    times = ['7:30 PM', '9:00 PM', '4:00 PM', '8:00 PM', '1:00 AM', '11:30 PM', '10:30 PM', '9:30 PM', '9:00 PM',
             '2:00 PM',
             '9:00 PM', '5:00 PM', '5:45 PM', '8:00 PM', '7:00 PM', '12:00 PM', '7:00 PM', '1:00 PM', '8:00 PM',
             '2:00 PM',
             '7:00 PM', '12:00 PM', '8:00 PM', '1:00 PM', '7:00 PM', '1:00 PM', '8:00 PM', '8:00 PM', '8:20 PM',
             '9:00 PM',
             '12:00 PM', '7:00 PM', '8:00 PM', '12:00 PM', '7:00 PM', '9:00 PM', '7:00PM', 'TBA']
    results_list = ['124 - 63', '95 - 75(W)', '97 - 57(W)', '93 - 67(W)', '83 - 68(W)', '104 - 61(W)', '107 - 75(W)',
               '71 - 56(W)', '67 - 76(L)', '95 - 50(W)', '83 - 74(W)', '73 - 71(W)', '100 - 103(L)', '85 - 42(W)',
               '102 - 74(W)', '63 - 75(L)', '89 - 86(W) OT', '107 - 56(W)', '93 - 87(W)', '96 - 83(W)', '85 - 68(W)',
               '90 - 82(W)', '91 - 72(W)', '62 - 77(L)', '80 - 78(W)', '83 - 76(W)', '78 - 86(L)', '97 - 73(W)',
               '65 - 41(W)', '74 - 63(W)', 'W', 'L', '90 - 83(W)', 'W', '', '', '', '']

    n_game_time, gt_warning = game_times(times)

    n_team_name = clean_opponent_names(schools_list)

    dt_year = set_year(dates_list, n_game_time)

    date_new, date_raw = pretty_dates(dt_year)

    GAMEDAY = get_latest_time(date_raw, n_team_name, gt_warning, results_list, date_new)

    res_record = record(results_list, schools_list)

    print(GAMEDAY)
    record_str = '%s-%s' % (res_record[0], res_record[1])
    print(record_str.center(30, ' '))

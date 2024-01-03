# TO-DO:
# Add all data to GUI and make it pretty
# Choose session in GUI
# Make less laggy (good luck)
# Could this use FFMPEG to create a full audio file for a race??? Could this be a video file that shows information? Could this be overlayed in vlc?

import vlc, requests, json, fastf1, time, tkinter as tk
from tkinter import *

def time_to_secs(utc):
    hrs = int(utc[11:13])
    mins = int(utc[14:16])
    secs = int(utc[17:19])
    totalsecs = hrs*3600 + mins*60 + secs
    return totalsecs

def get_start_time(ff1session):
    fastest = ff1session.laps.pick_laps(1)
    start_time = str(fastest[:1].LapStartDate).split('\n')[0]
    dash = start_time.find('-')
    start_time = start_time[(dash-4):]
    print(start_time)
    return start_time

def gui_update(root, colour, label1, name, number):
    label1.configure(text=f'{number} {name}', fg = colour)
    root.update_idletasks()
    root.update

def main():
    year = int(input('Enter year: '))
    gp = input('Enter GP: ')
    sessiontype = input('Enter session name: ')

    ff1session = fastf1.get_session(year, gp, sessiontype)
    ff1session.load()
    if ff1session.f1_api_support == False:
        print('\nError: Unsupported session (this is likely because it is from before 2018) \n')
        main()
    path = ff1session.api_path
    print(path)

    startsecs = time_to_secs(get_start_time(ff1session)) + 60
    startepoch = time.time()

    link = 'https://livetiming.formula1.com' + path


    resp = requests.get(link + 'TeamRadio.json') #gets JSON page with list of files
    urljson = json.loads(resp.text.encode('utf-8')) #Loads page as JSON

    #GUI setup
    root = tk.Tk()
    root.geometry("600x60")
    root.resizable(False, False)
    root.title("Team Radio Player")
    label1 = Label(root, text='', font = ("Arial", 30))
    label1.pack(ipadx=10, ipady=20)

    print('\nLoaded '+ str(len(urljson['Captures'])) + ' radio messages\n')
    input('Press enter to start...')
    print('Playing...\n')
    for i in range(0,len(urljson['Captures'])):
        path = link + urljson['Captures'][i]['Path'] #Gets URL of .mp3 file

        #Funky way of launching VLC to not get weird meaningless errors
        vlc_instance = vlc.Instance('-q')
        media_player = vlc_instance.media_player_new()
        media = vlc_instance.media_new(path)
        media_player.set_media(media)

        secs = time_to_secs(urljson['Captures'][i]['Utc'])
        if (secs - startsecs) - (time.time() - startepoch) > -60: #Skips radio messages from more than a minute before current time. This should allow time for overlapping messages while not playing messages from before start time
            while not (secs - startsecs <= time.time() - startepoch): # Waits until it is time for message
                time.sleep(1)
                root.update_idletasks()
                root.update()

            number = urljson['Captures'][i]['RacingNumber']
            driver = ff1session.get_driver(number)
            name = driver['FullName']
            team = driver['TeamName']
            colour = '#' + driver['TeamColor']
            img = driver['HeadshotUrl']
            gui_update(root, colour, label1, name, f'#{number}')
            print(f'\t#{number} {name} ({team})')

            media_player.play()
            #Waits until file is finished playing to play the next
            current_state = media.get_state()
            Ended = 6
            while current_state != Ended:
                current_state = media.get_state()
            gui_update(root, "white", label1, "", "")

if __name__ == '__main__':
    #root = tk.Tk()
    #root.geometry("600x400")
    main()
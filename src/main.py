from rcon.source import Client

import re
import time
import threading

from datetime import datetime, timedelta

from mpm import monitor


mordhau_monitor = monitor.MordhauMonitor()

@mordhau_monitor.on_join
def on_join(player: monitor.MordhauPlayer):
    playtime_data = mordhau_monitor.database.database.get_playtime_data(
        player
    )
    
    print(
        player.playfab, 
        player.name, 
        "has joined! Saved Playtime: {0}".format(
            playtime_data["total_playtime"]
        )
    )

@mordhau_monitor.on_leave
def on_leave(player: monitor.MordhauPlayer):
    print(
        player.playfab, 
        player.name, 
        "has left! Played for {0} second(s)".format(
            player.get_session_time()
        )
    )
    
    mordhau_monitor.save_player_playtime(player)
    

def format_time(seconds) -> tuple[int, int, int, int]:
    result =  (datetime(1, 1, 1) + timedelta(seconds=seconds))
    return result.day - 1, result.hour, result.minute, result.second


def chat_handler():
    with Client(
        mordhau_monitor.config.rcon.host, 
        mordhau_monitor.config.rcon.port,
        passwd=mordhau_monitor.config.rcon.password
    ) as client:
        client.run("listen", "chat")
        
        client.timeout = 1
        timeouts = 0
        
        while True:
            if timeouts >= 10:
                client.run("alive")
                timeouts = 0
                
            chat_data = None
            
            try:
                rcon_packet = client.read()
                
                if rcon_packet.payload.startswith(b"Chat: "):
                    chat_data = rcon_packet.payload.removeprefix(
                        b"Chat: "
                    ).decode()
                    
            except Exception as exc:
                assert str(exc) == "timed out"
                timeouts += 1
            
            if chat_data:
                playfab, name, *remaining = chat_data.split(", ")
                
                name = name.removeprefix(" ")
                
                remaining = ''.join(remaining).removesuffix("\n")
                
                channel_index = re.match(r'\((\w+)\) ', remaining).end(0)
                
                channel = remaining[0:channel_index]
                channel = channel.removeprefix(" ")
                
                message = remaining[channel_index::]
                
                if message.lower().startswith(".playtime"):
                    target_playfab_or_rank = message[len(".playtime") + 1::]
                    
                    if target_playfab_or_rank == "":
                        target_playfab_or_rank = None
                    
                    mordhau_player = mordhau_monitor.get_player_by_playfab(
                        playfab
                    )
                    
                    session_time = mordhau_player.get_session_time()
                    
                    real_playfab = ""
                    
                    playtime_data = 0
                    playtime_rank = 0
                    
                    if target_playfab_or_rank:
                        try:
                            playtime_rank = int(target_playfab_or_rank)
                            real_playfab, playtime_data = mordhau_monitor.database.database.get_playtime_data_by_rank(
                                playtime_rank
                            )
                        except:
                            try:
                                real_playfab = target_playfab_or_rank
                                playtime_data = mordhau_monitor.database.database.get_playtime_data(
                                    target_playfab_or_rank
                                )
                                
                                playtime_rank = mordhau_monitor.database.database.get_player_rank(
                                    target_playfab_or_rank
                                )
                            except:
                                target_playfab_or_rank = None
                                
                                playtime_data = mordhau_monitor.database.database.get_playtime_data(
                                    playfab
                                )
                                
                                playtime_rank = mordhau_monitor.database.database.get_player_rank(
                                    playfab
                                )
                    else:
                        playtime_data = mordhau_monitor.database.database.get_playtime_data(
                            playfab
                        )
                        
                        playtime_rank = mordhau_monitor.database.database.get_player_rank(
                            playfab
                        )
                    
                    total_playtime = playtime_data["total_playtime"] + session_time
                    
                    total_time = "%dd %dh %dm %ds" % format_time(
                        total_playtime
                    )
                    
                    if target_playfab_or_rank:
                        client.run(
                            "say",
                            f"[{real_playfab}]\nPlaytime: " + total_time + "\nRank: " + str(playtime_rank)
                        )
                    else:
                        client.run(
                            "say",
                            f"[{playfab} - {name}]\nPlaytime: " + total_time + "\nRank: " + str(playtime_rank)
                        )
                elif message.lower().startswith(".discord"):
                    client.run(
                        "say",
                        f"Join the 50's & Swifties Discord!\nhttps://discord.gg/wXBUn2qSFJ"
                    )


def playtime_handler():
    while True:
        try:
            mordhau_monitor.start_playtime_monitor()
        except Exception as err:
            print("PLAYTIME ERR", err)
            time.sleep(5)


if __name__ == "__main__":
    threading.Thread(target=playtime_handler).start()
    
    while True:
        try:
            chat_handler()
        except Exception as err:
            print("CHAT ERR", err)
            time.sleep(5)
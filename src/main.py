import time

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

#mordhau_monitor.database.database.establish()
#mordhau_monitor.database.save_playtime_data(
#    monitor.MordhauPlayer(
#        "7B24F811488928B4",
#        name="Watcher",
#        join_time=time.time() - 10
#    )
#)

mordhau_monitor.start_playtime_monitor()
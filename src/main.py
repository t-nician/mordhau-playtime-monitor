from mpm import monitor


mordhau_monitor = monitor.MordhauMonitor()


@mordhau_monitor.on_join
def on_join(player: monitor.MordhauPlayer):
    print(player.playfab, player.name, "has joined!")

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

mordhau_monitor.start_playtime_monitor()
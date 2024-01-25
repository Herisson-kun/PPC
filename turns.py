num_players = 2
running = True
while running:
    for player_id in range (1,num_players+1):
        turn_of = (player_id)%(num_players+1)
        print("Tour de :", turn_of)
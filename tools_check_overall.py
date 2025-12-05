from models import Player, PlayerStats, Position

# Create sample players with default stats and a range of ages
ages = list(range(18, 41))
players = []
for age in ages:
    # Use an arbitrary fielder position for batting sample
    p = Player(name=f"P{age}", position=Position.OUTFIELD, stats=PlayerStats(), age=age)
    players.append(p)

# Compute and print averages
tot = 0
for p in players:
    r = p.overall_rating
    print(f"age={p.age}, overall={r}")
    tot += r

avg = tot / len(players)
print(f"Average overall (ages 18-40): {avg:.2f}")

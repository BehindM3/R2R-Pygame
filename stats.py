class Stats:
    def __init__(self, health, damage, speed, xp_to_next_level=0):
        
        self.max_health = health
        self.health = health
        self.damage = damage
        self.speed = speed
        self.alive = True
        self.lvl = 1
        self.xp = 0
        self.xp_to_next_level = xp_to_next_level


    def take_damage(self, amount):
        if not self.alive:
            return False
        
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        
    def heal(self, amount):
        if not self.alive:
            return False
        
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
            return True
    
    def add_xp(self, amount):
        if not self.alive:
            return False
        
        self.xp += amount
        print(f"XP: {self.xp} / {self.xp_to_next_level}")

        if self.xp >= self.xp_to_next_level:
            self._level_up()
            return True

        return False
    
    def _level_up(self):
        self.lvl += 1
        
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)

        print(f"¡LEVEL UP! Eres nivel {self.lvl}")
        print(f"Próximo nivel a los {self.xp_to_next_level} XP")
class Stats:
    def __init__(self, health, damage, speed):
        
        self.max_health = health
        self.health = health
        self.damage = damage
        self.speed = speed
        self.alive = True

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
    
        
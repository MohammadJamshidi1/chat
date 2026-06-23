from django.db import models



class Chat(models.Model):
    participants = models.ManyToManyField("Accounts.Account" , related_name="chats")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]
        
        
    def __str__(self):
        users = list(self.participants.all()[:2])
        
        if len(users) >= 2:
            return f"{users[0].username} & {users[1].username}"
        return f"Chat {self.id}"
    

class Message(models.Model):
    chat = models.ForeignKey(Chat , on_delete=models.CASCADE , related_name="messages")
    sender = models.ForeignKey("Accounts.Account" , on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-sent_at"]
        
    
    def __str__(self):
        preview = self.content[:30] + "...." if len(self.content) > 30 else self.content
        return f"{self.sender.username} : {preview}"
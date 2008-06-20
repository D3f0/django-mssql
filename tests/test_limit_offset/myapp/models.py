from django.db import models

class Products(models.Model):
    productid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    notes = models.CharField(max_length=100)
    class Meta:
        db_table = u'Products'
        
    def __repr__(self):
        return "<Product %s: %s/%s (%s)" % (self.productid, self.name, self.color, self.notes)
        
    def __unicode__(self):
        return u"<Product %s: %s/%s (%s)" % (self.productid, self.name, self.color, self.notes)

from app.db import Base, SessionLocal, engine
from app.models import AccessibilityCheck, Review, User, Venue

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(User).count() == 0:
    jordan = User(id=1, name="Jordan Peters", role="Community Contributor",
                  wheelchair=True, no_stairs=True, review_count=42)
    db.add(jordan)

venues = [
    ("Harbour Lights Café", "18 Ariapita Avenue", "Café", "☕", "2 days ago", 27, 38, "Step-free,Accessible WC,Quiet",
     [("Entrance","Step-free, automatic door",96),("Restroom","Accessible stall on ground floor",91),("Seating","Wide aisle tables available",95),("Pathway","Smooth surface from sidewalk",93)],
     ('Maya R.','The entrance is genuinely step-free and the staff knew exactly where the accessible restroom was.')),
    ("The Green Room", "42 Woodbrook Lane", "Restaurant", "🍽️", "5 days ago", 57, 27, "Ramp,Wide doors,Accessible WC",
     [("Entrance","Permanent ramp; slight slope",89),("Restroom","Accessible restroom available",84),("Seating","Several wide-access tables",90),("Pathway","Smooth interior floor",88)],
     ('Daniel K.','Ramp works well. Call ahead for the quietest seating area during dinner.')),
    ("Queen’s Park Medical", "7 Savannah Drive", "Healthcare", "🏥", "today", 72, 55, "Lift,Accessible WC,Parking",
     [("Entrance","Level entrance + automatic door",99),("Restroom","Accessible restroom on each floor",97),("Lift","Large lift with tactile buttons",96),("Parking","Marked accessible bays",95)],
     ('Priya S.','Easy from parking to reception. Lift is spacious and clearly marked.')),
    ("Central Market", "12 Market Street", "Shopping", "🛍️", "3 weeks ago", 39, 52, "Side entrance,Accessible parking",
     [("Entrance","One step at main entrance",48),("Restroom","Accessibility not confirmed",55),("Pathway","Crowded at peak times",70),("Parking","Accessible bay nearby",76)],
     ('Alex T.','The side entrance may be easier, but information needs another on-site check.')),
    ("MovieHouse One", "88 Independence Avenue", "Entertainment", "🎬", "1 week ago", 82, 40, "Step-free,Accessible seating,Sensory",
     [("Entrance","Step-free lobby",94),("Seating","Wheelchair spaces + companion seats",92),("Restroom","Accessible restroom",89),("Sensory","Quiet screening times available",90)],
     ('Sam L.','Good accessible seating and staff were helpful without being intrusive.')),
]
for name,address,typ,icon,verified,x,y,tags,checks,review in venues:
    v = db.query(Venue).filter(Venue.name == name).first()
    if not v:
        v = Venue(name=name,address=address,type=typ,icon=icon,verified=verified,
                  map_x=x,map_y=y,tags=tags)
        db.add(v); db.flush()
        for cat,desc,pct in checks:
            db.add(AccessibilityCheck(venue_id=v.id,category=cat,description=desc,percent=pct))
        jordan = db.get(User,1)
        db.add(Review(venue_id=v.id,user_id=jordan.id,rating=5,category=checks[0][0],body=review[1]))
db.commit()
db.close()
print("AccessNow demo database seeded.")

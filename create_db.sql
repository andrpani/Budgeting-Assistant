CREATE TABLE "Purchase" (
    "ID"	    INTEGER NOT NULL UNIQUE,
	"Title"	    TEXT,
	"Date"	    TEXT,
	"Total"	    REAL,
	PRIMARY KEY("ID" AUTOINCREMENT)
);

CREATE TABLE "PurchaseItem" (
    "ID"        INTEGER NOT NULL UNIQUE,
    "Name"      TEXT,
    "Quantity"  INTEGER,
    "UnitPrice" REAL,
    "TotPrice"  REAL,
    "Info"      TEXT,
    "PurchaseID"  INTEGER NOT NULL,
    FOREIGN KEY("PurchaseID") REFERENCES "Purchase" ("ID")
        ON UPDATE SET NULL ON DELETE SET NULL,
    PRIMARY KEY("ID" AUTOINCREMENT)
);


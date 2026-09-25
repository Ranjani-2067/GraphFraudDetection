from __future__ import annotations
import csv, datetime as dt, os, random
from dataclasses import dataclass, field
from app.config import settings

ACCOUNT_TYPES=["savings","checking","business"]
DEVICE_TYPES=["mobile","desktop","atm","pos_terminal"]
CURRENCIES=["INR","USD"]
TXN_STATUSES=["completed","completed","completed","pending","flagged"]
CITIES=[("Chennai",13.0827,80.2707),("Bengaluru",12.9716,77.5946),("Mumbai",19.0760,72.8777),("Delhi",28.7041,77.1025),("Hyderabad",17.3850,78.4867),("Vellore",12.9165,79.1325)]

@dataclass
class GeneratedDataset:
    banks:list[dict]=field(default_factory=list); accounts:list[dict]=field(default_factory=list); devices:list[dict]=field(default_factory=list); ips:list[dict]=field(default_factory=list); transactions:list[dict]=field(default_factory=list)
    account_bank:list[dict]=field(default_factory=list); account_device:list[dict]=field(default_factory=list); account_ip:list[dict]=field(default_factory=list)
    suspicious_account_ids:set[str]=field(default_factory=set)

def _make_timestamp(rng, base, spread_days):
    return (base+dt.timedelta(days=rng.randint(0,spread_days),hours=rng.randint(0,23),minutes=rng.randint(0,59))).isoformat()

def generate_dataset(seed=None,num_accounts=None,num_normal_transactions=None):
    seed=settings.dataset_seed if seed is None else seed; num_accounts=settings.num_accounts if num_accounts is None else num_accounts; num_normal_transactions=settings.num_normal_transactions if num_normal_transactions is None else num_normal_transactions
    if num_accounts < 10 or num_normal_transactions < 20: raise ValueError("Use at least 10 accounts and 20 normal transactions for a meaningful prototype.")
    rng=random.Random(seed); ds=GeneratedDataset(); base=dt.datetime(2026,1,1)
    for i,name in enumerate(["Nilgiri National Bank","Coromandel Trust","Vellore Cooperative Bank","Union Bharat Bank"],1): ds.banks.append({"bank_id":f"BANK{i:03d}","bank_name":name,"branch_code":f"BR{1000+i}"})
    # Small pool of devices/IPs that a MINORITY of accounts incidentally share (e.g. a
    # shared home router, a family device) - kept deliberately small and low-probability
    # so it stays a realistic minority signal instead of touching most of the population.
    SHARED_POOL_SIZE=20; SHARED_TOUCH_PROB=0.10
    for i in range(1,SHARED_POOL_SIZE+1): ds.devices.append({"device_id":f"DEVSHR{i:04d}","device_type":rng.choice(DEVICE_TYPES)})
    for i in range(1,SHARED_POOL_SIZE+1):
        city,lat,lon=rng.choice(CITIES); ds.ips.append({"ip":f"10.{rng.randint(0,254)}.{rng.randint(0,254)}.{i%254+1}","geo_location":f"{city} ({lat:.4f},{lon:.4f})"})
    shared_devices=list(ds.devices); shared_ips=list(ds.ips)
    for i in range(1,num_accounts+1):
        aid=f"ACC{i:05d}"; ds.accounts.append({"account_id":aid,"name":f"Customer_{i:05d}","account_type":rng.choice(ACCOUNT_TYPES),"risk_score":0.0,"created_date":(base-dt.timedelta(days=rng.randint(30,1500))).date().isoformat()})
        ds.account_bank.append({"account_id":aid,"bank_id":rng.choice(ds.banks)["bank_id"]})
        # Every account gets its own unique personal device and IP by default - this
        # mirrors real banking behaviour where most customers use their own phone/home
        # network, so it never coincidentally collides with another account.
        personal_device={"device_id":f"DEVP{i:05d}","device_type":rng.choice(DEVICE_TYPES)}
        ds.devices.append(personal_device); ds.account_device.append({"account_id":aid,"device_id":personal_device["device_id"]})
        city,lat,lon=rng.choice(CITIES)
        personal_ip={"ip":f"172.16.{(i//254)%254}.{i%254+1}","geo_location":f"{city} ({lat:.4f},{lon:.4f})"}
        ds.ips.append(personal_ip); ds.account_ip.append({"account_id":aid,"ip":personal_ip["ip"]})
        # Only a small minority also touch the small shared pool - this is the realistic
        # "incidental sharing" case, kept rare enough that it doesn't drown out deliberate
        # fraud-ring device/IP sharing added later in this function.
        if rng.random()<SHARED_TOUCH_PROB: ds.account_device.append({"account_id":aid,"device_id":rng.choice(shared_devices)["device_id"]})
        if rng.random()<SHARED_TOUCH_PROB: ds.account_ip.append({"account_id":aid,"ip":rng.choice(shared_ips)["ip"]})
    ids=[a["account_id"] for a in ds.accounts]; counter=1
    def add(sender,receiver,amount,spread=180,status=None):
        nonlocal counter
        ds.transactions.append({"txn_id":f"TXN{counter:06d}","from_account":sender,"to_account":receiver,"amount":round(amount,2),"currency":rng.choice(CURRENCIES),"timestamp":_make_timestamp(rng,base,spread),"status":status or rng.choice(TXN_STATUSES)}); counter+=1
    for _ in range(num_normal_transactions):
        s,r=rng.sample(ids,2); add(s,r,rng.uniform(50,5000))
    for hub in rng.sample(ids,k=max(2,num_accounts//30)):
        for cp in rng.sample([a for a in ids if a!=hub],k=min(15,num_accounts-1)): add(cp,hub,rng.uniform(100,2000))
    for _ in range(max(3,num_accounts//25)):
        ring=rng.sample(ids,rng.choice([4,5,6])); ds.suspicious_account_ids.update(ring); amount=rng.uniform(8000,20000)
        for i,s in enumerate(ring): add(s,ring[(i+1)%len(ring)],amount*(0.9**i),5,"completed")
    for r in range(max(2,num_accounts//40)):
        ring=rng.sample(ids,rng.randint(3,5)); ds.suspicious_account_ids.update(ring); did=f"DEV_SHARED_{r:03d}"; ds.devices.append({"device_id":did,"device_type":"mobile"})
        for a in ring: ds.account_device.append({"account_id":a,"device_id":did})
        for _ in range(len(ring)): s,t=rng.sample(ring,2); add(s,t,rng.uniform(500,4000),20)
    for r in range(max(2,num_accounts//40)):
        ring=rng.sample(ids,rng.randint(3,5)); ds.suspicious_account_ids.update(ring); ip=f"192.168.{r%254}.{rng.randint(2,250)}"; city,lat,lon=rng.choice(CITIES); ds.ips.append({"ip":ip,"geo_location":f"{city} ({lat:.4f},{lon:.4f})"})
        for a in ring: ds.account_ip.append({"account_id":a,"ip":ip})
        for _ in range(len(ring)): s,t=rng.sample(ring,2); add(s,t,rng.uniform(500,4000),20)
    return ds

def write_dataset_to_csv(ds,out_dir=None):
    out_dir=out_dir or settings.data_dir; os.makedirs(out_dir,exist_ok=True)
    files={"banks.csv":(ds.banks,["bank_id","bank_name","branch_code"]),"accounts.csv":(ds.accounts,["account_id","name","account_type","risk_score","created_date"]),"devices.csv":(ds.devices,["device_id","device_type"]),"ips.csv":(ds.ips,["ip","geo_location"]),"transactions.csv":(ds.transactions,["txn_id","from_account","to_account","amount","currency","timestamp","status"]),"account_bank.csv":(ds.account_bank,["account_id","bank_id"]),"account_device.csv":(ds.account_device,["account_id","device_id"]),"account_ip.csv":(ds.account_ip,["account_id","ip"])}
    written={}
    for filename,(rows,fields) in files.items():
        path=os.path.join(out_dir,filename)
        with open(path,"w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        written[filename]=path
    return written

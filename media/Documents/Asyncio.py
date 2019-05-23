#!/usr/bin/env python
# coding: utf-8

# In[42]:


import asyncio
from time import sleep

def fun1(i):
    sleep(1)
    print("Task :"+str(i))
async def fun2(i):
    await asyncio.sleep(1)
    print("Task :"+str(i))
    
async def main():
    print("Sync")
    for i in range(1,10):    
        fun1(i)
    print ("Async")
    tasks = [fun2(i) for i in range(1, 10)]
    await asyncio.gather(*tasks)
await main()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





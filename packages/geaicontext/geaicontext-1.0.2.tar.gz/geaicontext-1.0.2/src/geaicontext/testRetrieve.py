import asyncio
from .tools.retrieve import retrieve_user_context

async def retrieve_ctx():
    
    id="CUST-123456"
    
    data=await retrieve_user_context(id)
    print(data)
    data=await retrieve_user_context(id)
    print(data)

def main():
    asyncio.run(retrieve_ctx())

if __name__ == "__main__":
    main()

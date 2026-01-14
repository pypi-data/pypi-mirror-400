import asyncio
import random
from .tools.save import save_user_context

async def save_dict_to_mongodb():
    
    id="CUST-243524"
    
    # Dictionary to save
    my_dict = {
        "name": "John Doe",
        "age": random.randint(25, 45),
        "email": "john@example.com",
        "city": "New York"
    }
    data=await save_user_context(id,my_dict)
    print(data)

def main():
    asyncio.run(save_dict_to_mongodb())

if __name__ == "__main__":
    main()

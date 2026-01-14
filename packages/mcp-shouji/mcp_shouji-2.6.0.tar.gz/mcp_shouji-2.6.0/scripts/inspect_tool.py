
import inspect
from mcp_shouji.server import get_system_info

def main():
    print(f"Type of get_system_info: {type(get_system_info)}")
    print(f"Dir of get_system_info: {dir(get_system_info)}")
    
    if hasattr(get_system_info, "fn"):
        print(f"Has fn attribute: {get_system_info.fn}")
    if hasattr(get_system_info, "run"):
        print(f"Has run attribute")
    if hasattr(get_system_info, "__call__"):
        print(f"Is callable")

if __name__ == "__main__":
    main()

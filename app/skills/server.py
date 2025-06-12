from fastmcp import FastMCP
from typing import Union, Tuple, Dict, Any, Optional
from all_skills import (
    fetch_weather
)

mcp = FastMCP("ITS-FRIDAY")

@mcp.tool()
async def get_weather(city: Optional[str] = None, mode: Optional[str] = "current") -> Union[Tuple[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict]]:
    """
    Get the weather condition at a specific city for 4 modes: ['current', 'forecast', 'search', 'history']
    If City is not given, it will use the location in the config file,
    and if in config file it is still not provided, the tool will use User's ip address to find the location, failed if User used a VPN!

    Input:
        - city: Optinal[str, None]
        - mode: Optional
    Return:
        - Success: A tuple with two dictionries, one is formatted, the other is raw (more information)
        - Failed: A tuple with first a string having a failed message and an empty dictionary
    """
    formatted, raw = await fetch_weather(city, mode)
    return formatted, raw

if __name__ == "__main__":
    mcp.run()
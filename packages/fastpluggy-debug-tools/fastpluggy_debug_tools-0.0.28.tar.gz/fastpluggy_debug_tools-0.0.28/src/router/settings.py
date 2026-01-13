from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_fastpluggy
from fastpluggy.core.repository.app_settings import update_db_settings

settings_router = APIRouter(prefix="/api", tags=["debug_tools_settings"])


class DebugPanelSettings(BaseModel):
    show_debug_panel_widget: bool


@settings_router.post("/settings", name="update_debug_settings")
async def update_debug_settings(
    settings: DebugPanelSettings,
    request: Request,
    db: Session = Depends(get_db),
    fast_pluggy=Depends(get_fastpluggy)
):
    """
    Update debug panel widget settings.
    """
    try:
        # Get the debug_tools plugin
        debug_plugin = fast_pluggy.get_plugin("debug_tools")
        if not debug_plugin or not debug_plugin.settings:
            raise HTTPException(status_code=404, detail="Debug tools plugin settings not found")
        
        # Update the settings
        new_params = {"show_debug_panel_widget": settings.show_debug_panel_widget}
        update_db_settings(current_settings=debug_plugin.settings, db=db, new_params=new_params)
        
        # Reload the application to apply changes
        fast_pluggy.load_app()
        
        return {"status": "success", "message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

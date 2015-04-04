UrT Position Plugin for BigBrotherBot [![BigBrotherBot](http://i.imgur.com/7sljo4G.png)][B3]
=====================================

Description
-----------
A [BigBrotherBot][B3] plugin which retrieves clients coordinates on UrT 4.2 modified servers. This plugin is meant to be 
used as subplugin since it doesn't provide commands or visual reaction to B3 events.

For plugin developers
---------------------
This plugin fires 2 new events:

* `EVT_CLIENT_MOVE` : when the player moves across the map (fired at most every `position_update_interval` seconds)
* `EVT_CLIENT_STANDING` : when the player is standing on the same location (fired at most every `position_update_interval` seconds)

When a new position is being retrieved the plugin a new attribute to the `b3.clients.Client` object: `position`. This 
attribute will hold the position coordinates:
 
* `client.position.x` : the X coordinate as floating point number
* `client.position.y` : the Y coordinate as floating point number
* `client.position.z` : the Z coordinate as floating point number

Download
--------
Latest version available [here](https://github.com/danielepantaleone/b3-plugin-urtposition/archive/master.zip).

Requirements
------------
This plugin is meant to work only with B3 version **1.10dev** or higher. No **1.9.x** version will be released since 
the plugin makes use of some new B3 core features which have been added in version 1.10 development branch. Also, the
plugin needs a modified UrT 4.2 server engine to work: you can ask more information on the B3 forums.

Installation
------------
Installation
------------
Drop the `urtposition` directory into `b3/extplugins`.  
Load the plugin in your `b3.ini` or `b3.xml` configuration file:
```xml
<plugin>
    <plugin name="urtposition" config="@b3/extplugins/urtposition/conf/plugin_urtposition.ini" />
</plugin>
```
```ini
[plugins]
location: @b3/extplugins/urtposition/conf/plugin_urtposition.ini
```

Changelog
---------
### 1.0 - 2015/04/04 - Fenix
- initial release

Support
-------
If you have found a bug or have a suggestion for this plugin, please report it on the [B3 forums][Support].

[B3]: http://www.bigbrotherbot.net/ "BigBrotherBot (B3)"
[Support]: http://forum.bigbrotherbot.net/ "Support topic on the B3 forums"
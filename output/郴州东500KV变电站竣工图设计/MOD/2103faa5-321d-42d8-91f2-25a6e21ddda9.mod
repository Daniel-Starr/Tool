<?xml version="1.0" encoding="utf-8"?>
<Device>
  <Entities>
    <Entity ID="2" Type="simple" Visible="false">
      <StretchedBody L="20.4824530537195" Normal="0,0,304.8" Array="2725,205.851854342757,2720.48245305369;2725,-194.148145657243,2720.48245305369;2275,-194.148145657243,2720.48245305369;2275,205.851854342757,2720.48245305369" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,-2720.4824530537,1" />
    </Entity>
    <Entity ID="3" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,2650.47143595605,156.120050950726,-150.000000000013,1" />
    </Entity>
    <Entity ID="4" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="2" Entity2="3" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="5" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,2650.47143595604,-143.879949049277,-150.000000000013,1" />
    </Entity>
    <Entity ID="6" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="4" Entity2="5" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="7" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,2350.47143595599,-143.879949049276,-150.000000000014,1" />
    </Entity>
    <Entity ID="8" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="6" Entity2="7" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="9" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,2350.47143595599,156.120050950727,-150.000000000014,1" />
    </Entity>
    <Entity ID="10" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="8" Entity2="9" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="11" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-2349.52856404396,156.120050950726,-150.000000000006,1" />
    </Entity>
    <Entity ID="12" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="10" Entity2="11" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="13" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-2349.52856404396,-143.879949049277,-150.000000000006,1" />
    </Entity>
    <Entity ID="14" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="12" Entity2="13" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="15" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-2649.52856404401,-143.879949049276,-150.000000000007,1" />
    </Entity>
    <Entity ID="16" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="14" Entity2="15" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="17" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-2649.52856404401,156.120050950727,-150.000000000007,1" />
    </Entity>
    <Entity ID="18" Type="boolean" Visible="true">
      <Boolean Type="Difference" Entity1="16" Entity2="17" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="19" Type="simple" Visible="false">
      <StretchedBody L="20.4824530537195" Normal="0,0,304.8" Array="-2275,205.851854342757,2720.4824530537;-2275,-194.148145657243,2720.4824530537;-2725,-194.148145657243,2720.4824530537;-2725,205.851854342757,2720.4824530537" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,-2720.4824530537,1" />
    </Entity>
    <Entity ID="20" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-2349.52856404396,156.120050950726,-150.000000000006,1" />
    </Entity>
    <Entity ID="21" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="19" Entity2="20" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="22" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-2349.52856404396,-143.879949049277,-150.000000000006,1" />
    </Entity>
    <Entity ID="23" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="21" Entity2="22" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="24" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-2649.52856404401,-143.879949049276,-150.000000000007,1" />
    </Entity>
    <Entity ID="25" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="23" Entity2="24" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="26" Type="simple" Visible="false">
      <Cylinder R="14.9999999999998" H="250" />
      <Color R="128" G="128" B="128" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-2649.52856404401,156.120050950727,-150.000000000007,1" />
    </Entity>
    <Entity ID="27" Type="boolean" Visible="true">
      <Boolean Type="Difference" Entity1="25" Entity2="26" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
  </Entities>
</Device>
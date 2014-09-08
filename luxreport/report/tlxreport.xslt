<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns="http://www.w3.org/1999/xhtml">
<xsl:output method="xml" indent="yes"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>
<xsl:template match="/">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>Releases</title>
        <style type="text/css">
            
body {
    font-family: 'Helvetica Neue', Arial, Helvetica, sans-serif;
    font-size: 14px;
    line-height: 18px;
    color: #393939;
}
td {
    font-size: 12px;
    border: 1px solid silver;
    vertical-align: top;
    padding: 5px;
}
.header {
    font-size: 14px;
    font-weight: bold;
    color: #f6f6f6;
    background-color: #23719f;
}
.header2 {
    font-size: 14px;
    font-weight: bold;
    color: #f6f6f6;
    background-color: #46b946;
}
.dimmed {
    background-color: #dbdbdb;
}

        </style>
    </head>
        <body>
            <table>
                <xsl:apply-templates/>
            </table>
        </body>
</html>
</xsl:template>
<xsl:template match="releases/*">
    <tr>
        <td class="header">File Name</td>
        <td class="header">Model</td>
        <td class="header">Ectaco Applications</td>
        <td class="header">3rd party Applications</td>
        <td class="header">Dictionary Voice</td>
        <td class="header">PhraseBook Voice</td>
        <td class="header">PhotoText input</td>
        <td class="header">ULearn pairs</td>
        <td class="header">ULearn-2 pairs</td>
        <td class="header">TTS SVOX</td>
        <td class="header">Google voice typing</td>
        <td class="header">Google Translate</td>
        <td class="header">Jibbigo</td>
        <td class="header2">SD: card Size</td>
    </tr>
    <tr>
        <td><xsl:value-of select="@project_id"/></td>
        <td><xsl:value-of select="@project_model"/></td>
        <xsl:apply-templates select="apps_ectaco"/>
        <xsl:apply-templates select="apps_other"/>
        <xsl:apply-templates select="voice_dictionary"/>
        <xsl:apply-templates select="voice_phrasebook"/>
        <xsl:apply-templates select="photo_text"/>
        <xsl:apply-templates select="ulearn"/>
        <xsl:apply-templates select="ulearn2"/>
        <xsl:apply-templates select="features"/>
        <xsl:apply-templates select="sdcard"/>
    </tr>
</xsl:template>
<xsl:template match="apps_ectaco">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="apps_other">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="voice_dictionary">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="voice_phrasebook">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="photo_text">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="ulearn">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="ulearn2">
    <td><xsl:value-of select="."/></td>
</xsl:template>
<xsl:template match="features">
    <td><xsl:value-of select="./feature_tts"/></td>
    <td><xsl:value-of select="./feature_sr"/></td>
    <td><xsl:value-of select="./feature_gt"/></td>
    <td><xsl:value-of select="./feature_jibbigo"/></td>
</xsl:template>
<xsl:template match="sdcard">
    <td class="dimmed"><xsl:value-of select="@sd_size"/></td>
</xsl:template>
</xsl:stylesheet>

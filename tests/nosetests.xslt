<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text"/>
    <xsl:template match="/">
Xunit Test Results - For: <xsl:value-of select="@name"/>

<xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="assemblies">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="testsuite">
Results for <xsl:value-of select="@name"/>

* Tests run: <xsl:value-of select="@tests"/>
* Failures: <xsl:value-of select="@failures"/>
* Skipped: <xsl:value-of select="@skip"/>
* Errors: <xsl:value-of select="@errors"/>

        <xsl:for-each select="testcase">
----
Class: <xsl:value-of select="@classname"/>
Name: <xsl:value-of select="@name"/>
Runtime: <xsl:value-of select="@time"/>
<xsl:choose>
<xsl:when test="not(*)">
PASSED
</xsl:when>
<xsl:when test="skipped">
SKIPPED
</xsl:when>
<xsl:otherwise>
FAILED
</xsl:otherwise>
</xsl:choose>
<xsl:for-each select="*">
	<xsl:if test="@message">
		<xsl:value-of select="@message"/>
	</xsl:if>
</xsl:for-each>
<xsl:for-each select="system-out">
	<xsl:value-of select="."/>
</xsl:for-each>
</xsl:for-each>
	</xsl:template>
</xsl:stylesheet>


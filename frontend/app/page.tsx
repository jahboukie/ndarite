'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import BackendStatus from '@/components/BackendStatus'
import {
  FileText,
  Shield,
  Zap,
  Users,
  CheckCircle,
  ArrowRight,
  Star,
  Clock,
  Globe
} from 'lucide-react'

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold gradient-text">NDARite</span>
          </div>

          <nav className="hidden md:flex items-center space-x-6">
            <Link href="#features" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Features
            </Link>
            <Link href="#pricing" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Pricing
            </Link>
            <Link href="#templates" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Templates
            </Link>
            <Link href="/login" className="text-sm font-medium hover:text-blue-600 transition-colors">
              Sign In
            </Link>
            <Button asChild>
              <Link href="/register">Get Started</Link>
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="gradient-bg py-20 px-4">
        <div className="container mx-auto text-center">
          <Badge variant="secondary" className="mb-4">
            🚀 Now in Beta - Generate Your First NDA Free
          </Badge>

          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Generate Legal NDAs in
            <span className="gradient-text"> Minutes, Not Hours</span>
          </h1>

          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Create legally-compliant, industry-specific Non-Disclosure Agreements through our
            intelligent questionnaire system. No expensive attorney consultations required.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button size="lg" asChild className="text-lg px-8">
              <Link href="/register">
                Start Creating NDAs
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild className="text-lg px-8">
              <Link href="/templates">View Templates</Link>
            </Button>
          </div>

          <div className="flex items-center justify-center space-x-8 text-sm text-gray-500">
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Legally Compliant
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Industry Specific
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              Electronic Signatures
            </div>
          </div>
        </div>
      </section>

      {/* Live Backend Integration Status */}
      <section className="py-12 px-4 bg-gray-50">
        <div className="container mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              🔥 Live Platform Status
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Real-time connection to our backend API showing live data integration
            </p>
          </div>
          <BackendStatus />
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Why Choose NDARite?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Professional-grade NDA generation with enterprise features at a fraction of the cost.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="text-center">
              <CardHeader>
                <Zap className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <CardTitle>Lightning Fast</CardTitle>
                <CardDescription>
                  Generate complete NDAs in under 5 minutes with our intelligent form system.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Shield className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <CardTitle>Legally Compliant</CardTitle>
                <CardDescription>
                  All templates reviewed by legal experts and compliant with current regulations.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Users className="h-12 w-12 text-purple-600 mx-auto mb-4" />
                <CardTitle>Multi-Party Support</CardTitle>
                <CardDescription>
                  Support for bilateral, unilateral, and multilateral agreements.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <FileText className="h-12 w-12 text-orange-600 mx-auto mb-4" />
                <CardTitle>Multiple Formats</CardTitle>
                <CardDescription>
                  Download as PDF or DOCX. Perfect for editing or immediate use.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Clock className="h-12 w-12 text-red-600 mx-auto mb-4" />
                <CardTitle>Version Control</CardTitle>
                <CardDescription>
                  Track changes, manage versions, and maintain document history.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Globe className="h-12 w-12 text-teal-600 mx-auto mb-4" />
                <CardTitle>Global Compliance</CardTitle>
                <CardDescription>
                  Templates for multiple jurisdictions and international agreements.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 bg-gray-50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that fits your needs. Upgrade or downgrade anytime.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free Plan */}
            <Card>
              <CardHeader>
                <CardTitle>Free</CardTitle>
                <CardDescription>Perfect for trying out NDARite</CardDescription>
                <div className="text-3xl font-bold">$0<span className="text-sm font-normal">/month</span></div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    3 documents per month
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Basic templates
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    PDF download
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Community support
                  </li>
                </ul>
                <Button className="w-full mt-6" variant="outline" asChild>
                  <Link href="/register">Get Started</Link>
                </Button>
              </CardContent>
            </Card>

            {/* Starter Plan */}
            <Card className="border-blue-500 relative">
              <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                Most Popular
              </Badge>
              <CardHeader>
                <CardTitle>Starter</CardTitle>
                <CardDescription>For small businesses and freelancers</CardDescription>
                <div className="text-3xl font-bold">$29<span className="text-sm font-normal">/month</span></div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    25 documents per month
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    All standard templates
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    PDF & DOCX download
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Electronic signatures
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Email support
                  </li>
                </ul>
                <Button className="w-full mt-6" asChild>
                  <Link href="/register?plan=starter">Start Free Trial</Link>
                </Button>
              </CardContent>
            </Card>

            {/* Professional Plan */}
            <Card>
              <CardHeader>
                <CardTitle>Professional</CardTitle>
                <CardDescription>For growing businesses</CardDescription>
                <div className="text-3xl font-bold">$99<span className="text-sm font-normal">/month</span></div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    100 documents per month
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    All templates + advanced
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Custom branding
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Priority support
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    Analytics dashboard
                  </li>
                </ul>
                <Button className="w-full mt-6" variant="outline" asChild>
                  <Link href="/register?plan=professional">Start Free Trial</Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-gray-50 py-12 px-4">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <FileText className="h-6 w-6 text-blue-600" />
                <span className="text-xl font-bold">NDARite</span>
              </div>
              <p className="text-gray-600 text-sm">
                Professional NDA generation platform for businesses of all sizes.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="/templates" className="hover:text-blue-600">Templates</Link></li>
                <li><Link href="/pricing" className="hover:text-blue-600">Pricing</Link></li>
                <li><Link href="/features" className="hover:text-blue-600">Features</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="/help" className="hover:text-blue-600">Help Center</Link></li>
                <li><Link href="/contact" className="hover:text-blue-600">Contact</Link></li>
                <li><Link href="/legal" className="hover:text-blue-600">Legal</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="/about" className="hover:text-blue-600">About</Link></li>
                <li><Link href="/blog" className="hover:text-blue-600">Blog</Link></li>
                <li><Link href="/careers" className="hover:text-blue-600">Careers</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t mt-8 pt-8 text-center text-sm text-gray-600">
            <p>&copy; 2024 NDARite. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

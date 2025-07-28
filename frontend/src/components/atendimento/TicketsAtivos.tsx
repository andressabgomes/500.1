import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from '@/hooks/use-toast';
import { 
  Plus, 
  Search, 
  Filter, 
  Eye, 
  Edit, 
  Trash2, 
  User, 
  Calendar, 
  Clock,
  AlertCircle,
  CheckCircle2,
  MessageSquare,
  Phone,
  Mail,
  MessageCircle,
  Star
} from 'lucide-react';
import { ticketAPI, customerAPI, userAPI } from '@/services/api';

interface Ticket {
  id: string;
  ticket_number: string;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed' | 'escalated';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  channel: 'whatsapp' | 'email' | 'phone' | 'chat';
  customer_id: string;
  assigned_to?: string;
  resolution?: string;
  satisfaction_rating?: number;
  satisfaction_comment?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

interface Customer {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
}

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

const TicketsAtivos = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [channelFilter, setChannelFilter] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium' as const,
    channel: 'whatsapp' as const,
    customer_id: '',
    assigned_to: '',
    tags: [] as string[],
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadTickets(),
        loadCustomers(),
        loadUsers(),
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadTickets = async () => {
    try {
      const response = await ticketAPI.getAll() as any;
      if (response.success) {
        setTickets(response.data);
      }
    } catch (error) {
      console.error('Error loading tickets:', error);
    }
  };

  const loadCustomers = async () => {
    try {
      const response = await customerAPI.getAll() as any;
      if (response.success) {
        setCustomers(response.data);
      }
    } catch (error) {
      console.error('Error loading customers:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await userAPI.getAll() as any;
      if (response.success) {
        setUsers(response.data);
      }
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  const handleCreateTicket = async () => {
    try {
      const response = await ticketAPI.create(formData) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Ticket criado com sucesso",
        });
        setIsCreateDialogOpen(false);
        resetForm();
        loadTickets();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao criar ticket",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao conectar com o servidor",
        variant: "destructive",
      });
    }
  };

  const handleDeleteTicket = async (ticketId: string) => {
    if (!confirm('Tem certeza que deseja excluir este ticket?')) return;
    
    try {
      const response = await ticketAPI.delete(ticketId) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Ticket excluído com sucesso",
        });
        loadTickets();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao excluir ticket",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao conectar com o servidor",
        variant: "destructive",
      });
    }
  };

  const handleAssignTicket = async (ticketId: string, userId: string) => {
    try {
      const response = await ticketAPI.assign(ticketId, userId) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Ticket atribuído com sucesso",
        });
        loadTickets();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao atribuir ticket",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao conectar com o servidor",
        variant: "destructive",
      });
    }
  };

  const handleResolveTicket = async (ticketId: string, resolution: string) => {
    try {
      const response = await ticketAPI.resolve(ticketId, resolution) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Ticket resolvido com sucesso",
        });
        loadTickets();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao resolver ticket",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao conectar com o servidor",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      priority: 'medium',
      channel: 'whatsapp',
      customer_id: '',
      assigned_to: '',
      tags: [],
    });
  };

  const getCustomerName = (customerId: string) => {
    const customer = customers.find(c => c.id === customerId);
    return customer?.name || 'Cliente não encontrado';
  };

  const getUserName = (userId: string) => {
    const user = users.find(u => u.id === userId);
    return user?.name || 'Não atribuído';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      case 'closed': return 'bg-gray-100 text-gray-800';
      case 'escalated': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'open': return 'Aberto';
      case 'in_progress': return 'Em Andamento';
      case 'resolved': return 'Resolvido';
      case 'closed': return 'Fechado';
      case 'escalated': return 'Escalado';
      default: return status;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'urgent': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'low': return 'Baixa';
      case 'medium': return 'Média';
      case 'high': return 'Alta';
      case 'urgent': return 'Urgente';
      default: return priority;
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'whatsapp': return <MessageCircle className="h-4 w-4" />;
      case 'email': return <Mail className="h-4 w-4" />;
      case 'phone': return <Phone className="h-4 w-4" />;
      case 'chat': return <MessageSquare className="h-4 w-4" />;
      default: return <MessageSquare className="h-4 w-4" />;
    }
  };

  const getChannelLabel = (channel: string) => {
    switch (channel) {
      case 'whatsapp': return 'WhatsApp';
      case 'email': return 'Email';
      case 'phone': return 'Telefone';
      case 'chat': return 'Chat';
      default: return channel;
    }
  };

  const filteredTickets = tickets.filter(ticket => {
    const matchesSearch = ticket.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ticket.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ticket.ticket_number.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || ticket.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || ticket.priority === priorityFilter;
    const matchesChannel = channelFilter === 'all' || ticket.channel === channelFilter;
    
    return matchesSearch && matchesStatus && matchesPriority && matchesChannel;
  });

  const statusCounts = {
    open: tickets.filter(t => t.status === 'open').length,
    in_progress: tickets.filter(t => t.status === 'in_progress').length,
    resolved: tickets.filter(t => t.status === 'resolved').length,
    closed: tickets.filter(t => t.status === 'closed').length,
    escalated: tickets.filter(t => t.status === 'escalated').length,
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header with Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-blue-600">{statusCounts.open}</div>
                <div className="text-sm text-muted-foreground">Abertos</div>
              </div>
              <AlertCircle className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-yellow-600">{statusCounts.in_progress}</div>
                <div className="text-sm text-muted-foreground">Em Andamento</div>
              </div>
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-green-600">{statusCounts.resolved}</div>
                <div className="text-sm text-muted-foreground">Resolvidos</div>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-600">{statusCounts.closed}</div>
                <div className="text-sm text-muted-foreground">Fechados</div>
              </div>
              <CheckCircle2 className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-red-600">{statusCounts.escalated}</div>
                <div className="text-sm text-muted-foreground">Escalados</div>
              </div>
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Actions */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Tickets Ativos</CardTitle>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Ticket
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Criar Novo Ticket</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="title">Título</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                      placeholder="Descreva o problema brevemente"
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">Descrição</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      placeholder="Descreva o problema detalhadamente"
                      rows={4}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="priority">Prioridade</Label>
                      <Select value={formData.priority} onValueChange={(value: any) => setFormData({...formData, priority: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione a prioridade" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Baixa</SelectItem>
                          <SelectItem value="medium">Média</SelectItem>
                          <SelectItem value="high">Alta</SelectItem>
                          <SelectItem value="urgent">Urgente</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="channel">Canal</Label>
                      <Select value={formData.channel} onValueChange={(value: any) => setFormData({...formData, channel: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o canal" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="whatsapp">WhatsApp</SelectItem>
                          <SelectItem value="email">Email</SelectItem>
                          <SelectItem value="phone">Telefone</SelectItem>
                          <SelectItem value="chat">Chat</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="customer_id">Cliente</Label>
                      <Select value={formData.customer_id} onValueChange={(value) => setFormData({...formData, customer_id: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o cliente" />
                        </SelectTrigger>
                        <SelectContent>
                          {customers.map(customer => (
                            <SelectItem key={customer.id} value={customer.id}>{customer.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="assigned_to">Atribuir a</Label>
                      <Select value={formData.assigned_to} onValueChange={(value) => setFormData({...formData, assigned_to: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o agente" />
                        </SelectTrigger>
                        <SelectContent>
                          {users.map(user => (
                            <SelectItem key={user.id} value={user.id}>{user.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <Button onClick={handleCreateTicket} className="w-full">
                    Criar Ticket
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar tickets..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os status</SelectItem>
                <SelectItem value="open">Aberto</SelectItem>
                <SelectItem value="in_progress">Em Andamento</SelectItem>
                <SelectItem value="resolved">Resolvido</SelectItem>
                <SelectItem value="closed">Fechado</SelectItem>
                <SelectItem value="escalated">Escalado</SelectItem>
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filtrar por prioridade" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas as prioridades</SelectItem>
                <SelectItem value="low">Baixa</SelectItem>
                <SelectItem value="medium">Média</SelectItem>
                <SelectItem value="high">Alta</SelectItem>
                <SelectItem value="urgent">Urgente</SelectItem>
              </SelectContent>
            </Select>
            <Select value={channelFilter} onValueChange={setChannelFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filtrar por canal" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os canais</SelectItem>
                <SelectItem value="whatsapp">WhatsApp</SelectItem>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="phone">Telefone</SelectItem>
                <SelectItem value="chat">Chat</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Tickets List */}
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-muted-foreground">Carregando tickets...</div>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredTickets.map((ticket) => (
                <Card key={ticket.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-semibold text-lg">{ticket.title}</h3>
                          <Badge variant="outline" className="text-xs">
                            {ticket.ticket_number}
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                          {ticket.description}
                        </p>
                        
                        <div className="flex flex-wrap gap-2 mb-3">
                          <Badge className={getStatusColor(ticket.status)}>
                            {getStatusLabel(ticket.status)}
                          </Badge>
                          <Badge className={getPriorityColor(ticket.priority)}>
                            {getPriorityLabel(ticket.priority)}
                          </Badge>
                          <Badge variant="outline" className="flex items-center gap-1">
                            {getChannelIcon(ticket.channel)}
                            {getChannelLabel(ticket.channel)}
                          </Badge>
                        </div>
                        
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            {getCustomerName(ticket.customer_id)}
                          </span>
                          <span className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            {ticket.assigned_to ? getUserName(ticket.assigned_to) : 'Não atribuído'}
                          </span>
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {new Date(ticket.created_at).toLocaleDateString('pt-BR')}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedTicket(ticket);
                            setIsViewDialogOpen(true);
                          }}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Select
                          value={ticket.assigned_to || ''}
                          onValueChange={(value) => handleAssignTicket(ticket.id, value)}
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue placeholder="Atribuir" />
                          </SelectTrigger>
                          <SelectContent>
                            {users.map(user => (
                              <SelectItem key={user.id} value={user.id}>{user.name}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteTicket(ticket.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Ticket Details Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Detalhes do Ticket</DialogTitle>
          </DialogHeader>
          {selectedTicket && (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-lg">{selectedTicket.title}</h3>
                <p className="text-sm text-muted-foreground">{selectedTicket.ticket_number}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Status</Label>
                  <Badge className={getStatusColor(selectedTicket.status)}>
                    {getStatusLabel(selectedTicket.status)}
                  </Badge>
                </div>
                <div>
                  <Label>Prioridade</Label>
                  <Badge className={getPriorityColor(selectedTicket.priority)}>
                    {getPriorityLabel(selectedTicket.priority)}
                  </Badge>
                </div>
              </div>
              
              <div>
                <Label>Descrição</Label>
                <p className="text-sm mt-1 p-3 bg-muted rounded-lg">{selectedTicket.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Cliente</Label>
                  <p className="text-sm mt-1">{getCustomerName(selectedTicket.customer_id)}</p>
                </div>
                <div>
                  <Label>Atribuído a</Label>
                  <p className="text-sm mt-1">{selectedTicket.assigned_to ? getUserName(selectedTicket.assigned_to) : 'Não atribuído'}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Canal</Label>
                  <div className="flex items-center gap-2 mt-1">
                    {getChannelIcon(selectedTicket.channel)}
                    <span className="text-sm">{getChannelLabel(selectedTicket.channel)}</span>
                  </div>
                </div>
                <div>
                  <Label>Criado em</Label>
                  <p className="text-sm mt-1">{new Date(selectedTicket.created_at).toLocaleString('pt-BR')}</p>
                </div>
              </div>
              
              {selectedTicket.resolution && (
                <div>
                  <Label>Resolução</Label>
                  <p className="text-sm mt-1 p-3 bg-green-50 rounded-lg">{selectedTicket.resolution}</p>
                </div>
              )}
              
              {selectedTicket.satisfaction_rating && (
                <div>
                  <Label>Avaliação</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star 
                          key={i} 
                          className={`h-4 w-4 ${i < selectedTicket.satisfaction_rating! ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                        />
                      ))}
                    </div>
                    <span className="text-sm">{selectedTicket.satisfaction_rating}/5</span>
                  </div>
                  {selectedTicket.satisfaction_comment && (
                    <p className="text-sm mt-2 p-2 bg-gray-50 rounded">{selectedTicket.satisfaction_comment}</p>
                  )}
                </div>
              )}
              
              {selectedTicket.status !== 'resolved' && selectedTicket.status !== 'closed' && (
                <div className="pt-4 border-t">
                  <Label>Resolução</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      placeholder="Descreva a resolução..."
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          const value = (e.target as HTMLInputElement).value;
                          if (value.trim()) {
                            handleResolveTicket(selectedTicket.id, value);
                            setIsViewDialogOpen(false);
                          }
                        }
                      }}
                    />
                    <Button
                      onClick={(e) => {
                        const input = (e.target as HTMLButtonElement).parentElement?.querySelector('input');
                        if (input && input.value.trim()) {
                          handleResolveTicket(selectedTicket.id, input.value);
                          setIsViewDialogOpen(false);
                        }
                      }}
                    >
                      Resolver
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TicketsAtivos;
